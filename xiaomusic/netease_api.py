import base64
import json
import os
import random
import binascii
import asyncio
import aiohttp
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Math.Numbers import Integer

# --- Constants for Encryption ---
# Weapi (Web)
MODULUS = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725"
    "152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312"
    "ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424"
    "d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
)
PUB_KEY = "010001"
NONCE = b"0CoJUm6Qyw8W8jud"
IV = b"0102030405060708"

# Eapi (Client)
EAPI_KEY = b"e82ckenh8dichen8"

# --- Encryption Helpers ---

from Crypto.Util.Padding import unpad

def aes_encrypt(text, key, mode='CBC'):
    if mode == 'CBC':
        cipher = AES.new(key, AES.MODE_CBC, IV)
        encrypted = cipher.encrypt(pad(text.encode('utf-8'), 16))
        return base64.b64encode(encrypted).decode('utf-8')
    elif mode == 'ECB':
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted = cipher.encrypt(pad(text.encode('utf-8'), 16))
        return binascii.hexlify(encrypted).decode('utf-8').upper()
    return ""

def aes_decrypt(text, key, mode='ECB'):
    if mode == 'ECB':
        cipher = AES.new(key, AES.MODE_ECB)
        try:
            # Check if input is hex string
            if isinstance(text, str):
                encrypted = binascii.unhexlify(text)
            else:
                encrypted = text
            decrypted = unpad(cipher.decrypt(encrypted), 16)
            return decrypted.decode('utf-8')
        except Exception as e:
            # print(f"Decrypt error: {e}")
            return None
    return ""

def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    rs = int(binascii.hexlify(text), 16) ** int(pub_key, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)

def create_secret_key(size):
    return binascii.hexlify(os.urandom(size // 2))[:16]

def weapi_encrypt(text):
    text = json.dumps(text)
    secret_key = create_secret_key(16)
    params = aes_encrypt(aes_encrypt(text, NONCE, 'CBC'), secret_key, 'CBC')
    enc_sec_key = rsa_encrypt(secret_key, PUB_KEY, MODULUS)
    return {
        'params': params,
        'encSecKey': enc_sec_key
    }

def eapi_encrypt(url, text):
    text = json.dumps(text)
    message = f"nobody{url}use{text}md5forencrypt"
    digest = hashlib.md5(message.encode('utf-8')).hexdigest()
    data = f"{url}-36cd479b6b5-{text}-36cd479b6b5-{digest}"
    return aes_encrypt(data, EAPI_KEY, 'ECB')

# --- Netease Music API Client ---

class NeteaseMusicApi:
    def __init__(self, cookie_str=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://music.163.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        if cookie_str:
            self.headers['Cookie'] = cookie_str
        else:
            # Default Cookie provided by user
            self.headers['Cookie'] = 'JSESSIONID-WYYY=pC8h1Kib%2FGlTevnMeNsVnus%2B%5CZP%5COtdzfIgwKIdwnhxOCx3wqewm%2BDFWp5oXCNkAffP%5CxVdtStjQgcwODjWaKIUuhC0UEFgcwZgKBsrcEolGFqBK%2BDyVt1sr1Eg2s2W3wb4gEq%2FeWayPXg1Ih57aWh17tXuCdGhZaB2sS9IGWUAhHr%2Bl%3A1768053759633; _iuqxldmzr_=32; _ntes_nnid=790e6004a1076e363d469b1825867d15,1768051959648; _ntes_nuid=790e6004a1076e363d469b1825867d15; Hm_lvt_1483fb4774c02a30ffa6f0e2945e9b70=1768051960; HMACCOUNT=D765C35E3278F932; NMTID=00OuCsuROnNa2iKXEGEuixjRXYUY1oAAAGbqBvjVw; WEVNSM=1.0.0; WNMCID=bjhseo.1768051960712.01.0; WM_NI=rzU0983JHMeLVIX4%2F80PE6DAhdzrT2at%2BFhF5ZvjesOgVuT%2BwtukTwv2JTQkTxFuZBlSRpWDYNFk6tp6OAObcnwmJQziMsNJtFxCwUw6tYr4rh0%2B%2FVTBYgtG%2FxufdYsOQ0I%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed2d34b8c929886c97ab5928aa7c55b939e9f83c766ada68aa6f37ef8b8e5adcf2af0fea7c3b92ab2a69bd1bc34f19688aee848969798d5ae34f4908bd7c74bacbcb693d73aa3ace5a7eb4ef786ba8be8798db99a96d721b5acbb8cd77db6ee86b5d46198a88a96d94ab08d9e91d6509b928a8cb580b4ea81a2ce6aa1b2b98ec95bbab78394cd42b89ab8a4f65fb5eabcbaf140b2b800ccae5e989e9788f74deda8bb87e753b1919fd1cc37e2a3; WM_TID=YxHsktwKSzxFAQFVRAKSm5iEUpv5gNcC; __snaker__id=caperbp27cjyx5SO; sDeviceId=YD-kWPPsEnIL6hBRlRQQEPCm5jUFou93gTd; gdxidpyhxdE=lc%5CZlUMIKgyiJyw%2BX4PiIKpcwKO2oYz8dvwOCgKXux7iYBIG6rqj1lo5lxke1co%2F0vkzCR%5CIAKpoOAzD6OiKEAHA1gGvan%2Fqg%2BCgO0U0%2B0aJVB3rXwMocDX8lUbMeqpOik65M15AhUxBl9VmrfVeQ4icUxNtXBdAYrH5H3IqY5s0p2x8%3A1768052864189; __csrf=5ccd8f085f26f849a54c2d8157f5cc7e; MUSIC_U=00FA9FF279195FE1EA9FF017F9FD99B01C4B296EE27CDEC46ACD61281F9AF22D1471E2D66D8609ABF027AAA570A365208B83DBD88A51265A9FE112D3EBE0F1685BCF18C07FCAE75C49721F02087DF1BA0365D0615E250D9B39BADC90BB8A7505A69829E9918DFD91D73971549B175FF2F69A908741CF40A9EBAC0E7B2FC020CD5A2A1D39C8A3A3D0EEB524693F582161217CB6C235CCBBFDA6F3CCFF3809D244D662A09F73F358A0F7B870A37BA940A970AF4173A4156E1044218AA50E40A85F20D7D0E608BA3A0DF363D8187D942B2E2325349949D6D4052FC545BB64D230BC5225B0C443D29C4699F4B0B1EF50DEA543722DB0D031C28D0A73CA7EBDD029E12DCB68CF3B56339FF7AAD9E6BCFC97E3144CA52E902F477F24869627FFD57F5EB7CADDC604EBFE29BCDDF379E38064B7E2BCBF5C007E200C5224467F02D83BF07A52C9183A4C1EE06BF14F20AB585179E05ED9144433E1CC0C6B9283CB05592492A990FC03959152361E2566E2B1DE9D8E964C9F722823CDB63DBAF7B23864E544DA82D8B24C05D4C1184FFBBB87DB4DB3; ntes_utid=tid._.DFFTChI4tq1FExFBBQfT3sjVQsq9izVi._.0; Hm_lpvt_1483fb4774c02a30ffa6f0e2945e9b70=1768051989; ntes_kaola_ad=1'

    async def _request(self, method, url, data=None, crypto='weapi'):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            if method == 'POST':
                if crypto == 'weapi':
                    data = weapi_encrypt(data)
                    async with session.post(url, data=data) as resp:
                        return await resp.json(content_type=None)
                elif crypto == 'eapi':
                    # Eapi uses a specific format for params: https://interface.music.163.com/eapi/ -> /api/
                    if 'interface.music.163.com/eapi/' in url:
                        path = url.replace('https://interface.music.163.com/eapi/', '/api/')
                    else:
                        path = url.replace('https://interface.music.163.com', '/api')
                    
                    encrypted_data = eapi_encrypt(path, data)
                    payload = {'params': encrypted_data}
                    async with session.post(url, data=payload) as resp:
                        content = await resp.read()
                        try:
                            # Try to decode as json directly
                            return json.loads(content)
                        except:
                            # If failed, try decrypt
                            decrypted = aes_decrypt(content, EAPI_KEY, 'ECB')
                            if decrypted:
                                return json.loads(decrypted)
                            raise Exception(f"Failed to decode response: {content[:100]}...")
            else:
                async with session.get(url) as resp:
                    return await resp.json(content_type=None)

    async def search(self, keyword, limit=5, offset=0, type_id=1):
        """
        type_id: 1: 单曲
        """
        url = 'https://music.163.com/weapi/cloudsearch/get/web'
        data = {
            's': keyword,
            'type': type_id,
            'limit': limit,
            'offset': offset,
            'csrf_token': ''
        }
        return await self._request('POST', url, data, crypto='weapi')

    async def get_song_url(self, song_id, br=320000):
        """
        Use Web API (weapi)
        """
        url = 'https://music.163.com/weapi/song/enhance/player/url/v1'
        data = {
            'ids': [song_id],
            'level': 'standard',
            'encodeType': 'aac',
            'csrf_token': ''
        }
        if br > 320000:
             data['level'] = 'hires'
        elif br == 320000:
             data['level'] = 'exhigh'
        
        return await self._request('POST', url, data, crypto='weapi')

    async def get_song_url_v1(self, song_id, level='exhigh'):
        """
        Use Client API (eapi) for potentially better quality
        level: standard, exhigh, lossless, hires
        """
        url = 'https://interface.music.163.com/eapi/song/enhance/player/url/v1'
        data = {
            'ids': [str(song_id)],
            'level': level,
            'encodeType': 'flac',
            'e_r': True
        }
        return await self._request('POST', url, data, crypto='eapi')

# --- Main Test Execution ---

async def main():
    print("=== 网易云音乐 API 测试 (整合 Weapi & Eapi) ===")
    
    cookie = os.environ.get('NETEASE_COOKIE')
    if not cookie:
        print("提示: 未检测到环境变量 NETEASE_COOKIE。")
        print("将使用内置的默认 Cookie (已包含 VIP 权限)。")
        user_input = input("按回车键继续使用默认 Cookie，或输入新 Cookie 进行覆盖: ").strip()
        if user_input:
            cookie = user_input

    api = NeteaseMusicApi(cookie)

    while True:
        keyword = input("\n请输入搜索关键词 (输入 'q' 退出): ").strip()
        if keyword.lower() == 'q':
            break
        
        if not keyword:
            continue

        try:
            print(f"正在搜索 '{keyword}'...")
            search_result = await api.search(keyword)
            
            songs = search_result.get('result', {}).get('songs', [])
            if not songs:
                print("未找到结果。")
                print(search_result)
                continue

            print("\n搜索结果:")
            for i, song in enumerate(songs):
                artists = ", ".join([ar['name'] for ar in song['ar']])
                album = song['al']['name']
                print(f"{i+1}. {song['name']} - {artists} (专辑: {album}) [ID: {song['id']}]")
            
            choice = input("\n请输入要获取链接的歌曲序号 (1-5): ").strip()
            if not choice.isdigit() or not (1 <= int(choice) <= len(songs)):
                print("无效的选择。")
                continue

            selected_song = songs[int(choice) - 1]
            song_id = selected_song['id']
            print(f"正在获取 '{selected_song['name']}' 的下载链接...")
            
            # Try EAPI first (Client API)
            print("尝试使用客户端接口 (EAPI) 获取高音质...")
            url_result = await api.get_song_url_v1(song_id, level='lossless')
            data_list = url_result.get('data', [])
            
            if not data_list or not data_list[0].get('url'):
                print("EAPI 获取失败或无链接，尝试网页接口 (WEAPI)...")
                url_result = await api.get_song_url(song_id, br=999000)
                data_list = url_result.get('data', [])

            if data_list and data_list[0].get('url'):
                song_data = data_list[0]
                print(f"\n成功获取链接!")
                print(f"URL: {song_data['url']}")
                print(f"音质/类型: {song_data['level']} / {song_data['type']}")
                print(f"大小: {song_data['size']} bytes")
                print(f"费用: {song_data['fee']} (0: 免费, 1: VIP, 8: 低音质免费)")
            else:
                print("\n无法获取链接。可能原因：需要会员权限、歌曲下架或 Cookie 无效。")
                print(f"API 返回: {url_result}")

        except Exception as e:
            print(f"发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
