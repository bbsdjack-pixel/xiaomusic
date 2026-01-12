import asyncio
import logging
import socket
import os
import uuid
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import aiohttp
from aiohttp import web

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SSDP 配置
SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_MX = 2
SSDP_ST = "urn:schemas-upnp-org:service:AVTransport:1"

# 临时文件存储
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "media")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_local_ip():
    """获取本机局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class SSDPDiscovery:
    def __init__(self):
        self.devices = []

    async def discover(self, timeout=3):
        self.devices = []
        
        # 构造 M-SEARCH 消息
        msg = \
            'M-SEARCH * HTTP/1.1\r\n' \
            'HOST: {}:{}\r\n' \
            'MAN: "ssdp:discover"\r\n' \
            'MX: {}\r\n' \
            'ST: {}\r\n' \
            '\r\n'.format(SSDP_ADDR, SSDP_PORT, SSDP_MX, SSDP_ST).encode('utf-8')

        # 创建 UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        try:
            sock.sendto(msg, (SSDP_ADDR, SSDP_PORT))
            
            # 异步接收
            loop = asyncio.get_event_loop()
            start_time = loop.time()
            
            while loop.time() - start_time < timeout:
                try:
                    data, addr = await loop.run_in_executor(None, sock.recvfrom, 1024)
                    await self.process_response(data.decode('utf-8', errors='ignore'))
                except socket.timeout:
                    break
                except Exception as e:
                    logger.error(f"Socket error: {e}")
                    break
        finally:
            sock.close()
            
        return self.devices

    async def process_response(self, response):
        headers = {}
        for line in response.split('\r\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().upper()] = value.strip()
        
        location = headers.get('LOCATION')
        if location:
            await self.fetch_device_info(location)

    async def fetch_device_info(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        self.parse_device_xml(content, url)
        except Exception as e:
            logger.error(f"Error fetching device info from {url}: {e}")

    def parse_device_xml(self, content, location_url):
        try:
            root = ET.fromstring(content)
            ns = {'n': 'urn:schemas-upnp-org:device-1-0'}
            
            # 为了简单起见，移除命名空间或处理它
            # 这里我们尝试查找 friendlyName 和 AVTransport 服务
            
            device = root.find(".//n:device", ns)
            if device is None:
                # 尝试不带命名空间
                device = root.find(".//device")
            
            if device is None:
                return

            friendly_name = device.findtext("n:friendlyName", namespaces=ns)
            if not friendly_name:
                friendly_name = device.findtext("friendlyName")

            # 查找 AVTransport 服务
            service_list = device.findall(".//n:service", ns)
            if not service_list:
                service_list = device.findall(".//service")
                
            control_url = None
            service_type = None

            for service in service_list:
                s_type = service.findtext("n:serviceType", namespaces=ns) or service.findtext("serviceType")
                if "AVTransport" in s_type:
                    c_url = service.findtext("n:controlURL", namespaces=ns) or service.findtext("controlURL")
                    if c_url:
                        control_url = urljoin(location_url, c_url)
                        service_type = s_type
                        break
            
            if friendly_name and control_url:
                # 避免重复
                for d in self.devices:
                    if d['control_url'] == control_url:
                        return
                        
                self.devices.append({
                    'friendly_name': friendly_name,
                    'host': urlparse(location_url).netloc,
                    'control_url': control_url,
                    'service_type': service_type
                })
                logger.info(f"Found device: {friendly_name}")

        except Exception as e:
            logger.error(f"XML parse error: {e}")

class UPnPController:
    @staticmethod
    async def send_soap_action(control_url, service_type, action, args):
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
            <s:Body>
                <u:{action} xmlns:u="{service_type}">
                    {args}
                </u:{action}>
            </s:Body>
        </s:Envelope>"""

        headers = {
            'Content-Type': 'text/xml; charset="utf-8"',
            'SOAPAction': f'"{service_type}#{action}"'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(control_url, data=soap_body, headers=headers) as resp:
                    resp_text = await resp.text()
                    if resp.status != 200:
                        logger.error(f"SOAP Error {resp.status}: {resp_text}")
                        return False, f"HTTP Error {resp.status}"
                    return True, "Success"
        except Exception as e:
            logger.error(f"SOAP Request Error: {e}")
            return False, str(e)

    @staticmethod
    async def set_av_transport_uri(control_url, service_type, media_url):
        args = f"""
        <InstanceID>0</InstanceID>
        <CurrentURI>{media_url}</CurrentURI>
        <CurrentURIMetaData></CurrentURIMetaData>
        """
        return await UPnPController.send_soap_action(control_url, service_type, "SetAVTransportURI", args)

    @staticmethod
    async def play(control_url, service_type):
        args = """
        <InstanceID>0</InstanceID>
        <Speed>1</Speed>
        """
        return await UPnPController.send_soap_action(control_url, service_type, "Play", args)

    @staticmethod
    async def pause(control_url, service_type):
        args = """
        <InstanceID>0</InstanceID>
        """
        return await UPnPController.send_soap_action(control_url, service_type, "Pause", args)
    
    @staticmethod
    async def stop(control_url, service_type):
        args = """
        <InstanceID>0</InstanceID>
        """
        return await UPnPController.send_soap_action(control_url, service_type, "Stop", args)

# Web Handlers
async def index_handler(request):
    with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r', encoding='utf-8') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def scan_handler(request):
    discovery = SSDPDiscovery()
    devices = await discovery.discover()
    return web.json_response({'devices': devices})

async def play_handler(request):
    reader = await request.multipart()
    
    # 简单的 multipart 解析
    field = await reader.next()
    filename = None
    
    # 处理文件上传
    if field.name == 'file':
        filename = field.filename
        # 清理旧文件 (可选)
        for f in os.listdir(UPLOAD_DIR):
            try:
                os.remove(os.path.join(UPLOAD_DIR, f))
            except: 
                pass
                
        # 保存新文件
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                f.write(chunk)
    
    # 获取其他字段
    device_url = None
    service_type = None
    
    while True:
        field = await reader.next()
        if field is None:
            break
        if field.name == 'device_url':
            device_url = await field.text()
        elif field.name == 'service_type':
            service_type = await field.text()

    if not filename or not device_url:
        return web.json_response({'success': False, 'message': 'Missing file or device'})

    # 构造媒体 URL
    local_ip = get_local_ip()
    port = request.app['port']
    media_url = f"http://{local_ip}:{port}/files/{filename}"
    logger.info(f"Casting media: {media_url}")

    # 发送 DLNA 命令
    success, msg = await UPnPController.set_av_transport_uri(device_url, service_type, media_url)
    if not success:
        return web.json_response({'success': False, 'message': f'SetURI failed: {msg}'})
        
    success, msg = await UPnPController.play(device_url, service_type)
    if not success:
        return web.json_response({'success': False, 'message': f'Play failed: {msg}'})

    return web.json_response({'success': True, 'message': 'Playing'})

async def control_handler(request):
    data = await request.json()
    action = data.get('action')
    device_url = data.get('device_url')
    service_type = data.get('service_type')
    
    if action == 'pause':
        success, msg = await UPnPController.pause(device_url, service_type)
    elif action == 'stop':
        success, msg = await UPnPController.stop(device_url, service_type)
    else:
        return web.json_response({'success': False, 'message': 'Unknown action'})
        
    return web.json_response({'success': success, 'message': msg})

def main():
    app = web.Application()
    app.router.add_get('/', index_handler)
    app.router.add_get('/api/scan', scan_handler)
    app.router.add_post('/api/play', play_handler)
    app.router.add_post('/api/control', control_handler)
    app.router.add_static('/files', UPLOAD_DIR)
    
    port = 8090
    app['port'] = port
    
    print(f"Server running at http://localhost:{port}")
    web.run_app(app, port=port)

if __name__ == '__main__':
    main()
