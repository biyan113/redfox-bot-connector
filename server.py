#!/usr/bin/env python3
"""RedFox MCP server, stdio transport, Python standard library only."""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def key():
    value = os.environ.get('REDFOX_API_KEY')
    if value: return value
    p = ROOT / '.env'
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith('REDFOX_API_KEY='): return line.split('=', 1)[1].strip()
    raise ValueError('请设置 REDFOX_API_KEY 或在项目目录的 .env 中配置')

def query(path, body):
    if not isinstance(path, str) or not path.startswith('/story/api/') or '?' in path or '#' in path or '..' in path:
        raise ValueError('仅允许 /story/api/ 下的接口路径')
    if not isinstance(body, dict): raise ValueError('body 必须为 JSON 对象')
    req = urllib.request.Request('https://redfox.hk' + path, data=json.dumps(body, ensure_ascii=False).encode(), headers={'Content-Type':'application/json','REDFOX_API_KEY':key()}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read(4_000_001)
            if len(data) > 4_000_000: raise ValueError('响应超过 4 MB')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        raise ValueError('RedFox HTTP 错误：%s' % e.code)
    except urllib.error.URLError:
        raise ValueError('无法连接 RedFox，请检查网络')

TOOLS = [
 {'name':'search_douyin_users','description':'通过已核实的 RedFox 接口按关键词搜索抖音账号。调用可能产生费用。','inputSchema':{'type':'object','properties':{'keyword':{'type':'string'},'offset':{'type':'integer','minimum':0,'default':0}},'required':['keyword'],'additionalProperties':False}},
 {'name':'redfox_post','description':'调用 RedFox 文档中已确认的 POST 接口。先查官方文档获取准确路径和参数。调用可能产生费用。','inputSchema':{'type':'object','properties':{'path':{'type':'string','description':'以 /story/api/ 开头的官方接口路径'},'body':{'type':'object','description':'官方文档要求的 JSON 请求体'}},'required':['path','body'],'additionalProperties':False}}
]

def handle(msg):
    method=msg.get('method'); params=msg.get('params') or {}
    if method == 'initialize': return {'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'redfox-bot-connector','version':'0.1.0'}}
    if method == 'ping': return {}
    if method == 'tools/list': return {'tools':TOOLS}
    if method == 'tools/call':
        name=params.get('name'); args=params.get('arguments') or {}
        try:
            if name == 'search_douyin_users':
                keyword=args.get('keyword'); offset=args.get('offset',0)
                if not isinstance(keyword,str) or not keyword.strip() or not isinstance(offset,int) or isinstance(offset,bool) or offset<0: raise ValueError('请提供关键词及非负整数 offset')
                data=query('/story/api/dyData/searchUser',{'keyword':keyword,'offset':offset})
            elif name == 'redfox_post': data=query(args.get('path'),args.get('body'))
            else: raise ValueError('未知工具')
            return {'content':[{'type':'text','text':json.dumps(data,ensure_ascii=False)}]}
        except (ValueError, TimeoutError, json.JSONDecodeError) as e:
            return {'isError':True,'content':[{'type':'text','text':str(e)}]}
    raise LookupError('Method not found')

def main():
    for line in sys.stdin:
        try:
            msg=json.loads(line)
            if 'id' not in msg: continue
            try: result={'jsonrpc':'2.0','id':msg['id'],'result':handle(msg)}
            except LookupError: result={'jsonrpc':'2.0','id':msg['id'],'error':{'code':-32601,'message':'Method not found'}}
            print(json.dumps(result,ensure_ascii=False),flush=True)
        except Exception:
            print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid request'}}),flush=True)
if __name__=='__main__': main()
