from __future__ import unicode_literals
from functools import reduce
#latex 2img에 필요함
import io
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import operator
#img 2 latex에 필요함
import sys
import base64   
import requests
import json
import matplotlib.pyplot as plt
from sympy import *
from matplotlib import rcParams
rcParams['font.family'] = 'NanumGothic'#'sans-serif'
rcParams['text.usetex'] = True
rcParams['text.latex.unicode'] = True
rcParams['text.latex.preamble'] = [r'\usepackage{mathtools}',r'\usepackage{kotex}',r'\usepackage{txfonts}']
lendict = {}
defaultfunction = ['exp','sin','cos','tan','csc'] #등등 추가바람
relationals = ['<','>','=',r'\leq',r'\geq']
class MyException(Exception):
    def __init__(self, msg):
        self.msg = msg
def getidx(string, str_list,begin='',end=''):
    #== 리스트 변환 ==
    #print(string,str_list)
    if isinstance(str_list, str):
        str_list = [str_list]

    for idx in range(len(str_list)):
        if isinstance(str_list[idx], list):
            if isinstance(str_list[idx][0],int):  
                if getbool(str_list[idx], string[:1],begin,end):
                    return (idx, 1)
            else:
                idx2 = getidx( string,str_list[idx],begin,end)[0]
                if idx2 is not None:
                    return (idx, len(str_list[idx][idx2]))
        elif string[:len(str_list[idx])] == str_list[idx]:
            return (idx, len(str_list[idx]))
    return (None,None)

# begin end제약조건
# 1. begin != end
# 2. '\\' not in begin and '\\' not in end
# 
# param = begin이나 end일 수 있다. 왜냐면 우선순위가 더 높기에
# param에 find_escaped(begin)이나 end는 None이여야 한다.

def getlen(string, parsed_list, row, begin,end):
    #==디버깅==
    #print(string,parsed_list)
    if string in lendict:
        if row in lendict[string] :
            return lendict[string][row]
        else:
            flag_1 = True
            flag_2 = False
    else:
        flag_1 = False
        flag_2 = True
    parsed = [i[0] for i in parsed_list[row]]
    loopback = [i[1] for i in parsed_list[row]]
    noparam = [i[2] for i in parsed_list[row]]
    times = [i[3] for i in parsed_list[row]]
    loopback_len = len(loopback)
    beforeback = None
    cnt = [0 for i in range(loopback_len)]
    #==디버깅==
    #print(string,[parsed[0]])
    #== 제약조건 ==
    if getidx(string,[parsed[0]],begin,end)[0] is None:
        raise MyException("'"+parsed[0]+"' Must Be First Of String")
    i= 0
    col = 0
    prev = -1
    str_len = len(string)
    waslooped = False
    start =0
    #== 루프시작 ==
    while i < str_len:
        str_list = [parsed_list[i][0][0]  for i in range(len(parsed_list))]
        str_list.insert(row,parsed[col])
        str_list = str_list[prev+1:]
        # if col!= 0 and parsed[col-1][-len(argleft):] == argleft  and parsed[col][:len(argright)] == argright:
        #     idx = findpair_escaped(string[i-len(argleft):],argleft,argright)
        #     # print("argrrrrr2:",string[i-len(argleft) +idx - len(argright):i-len(argleft)+idx - len(argright)+len(parsed[col])])
        #     # print('parsed[col]:',parsed[col])\
        #     if idx is not None  and string[i-len(argleft) +idx - len(argright):i-len(argleft)+idx - len(argright)+len(parsed[col])] == parsed[col]:
        #         i = i-len(argleft) +idx - len(argright)
        #         idx = row-(prev+1) 
        #         idx_len = len(parsed[col])
        #     else:
        #         #argleft, right들은 떨어질 수 없다 이말이야
        #         return None
        # else:
        idx,idx_len = getidx(string[i:],str_list,begin,end)
         
        #== 디버깅
        #print(string[i:],str_list,idx)
        if idx is not None:
            if idx == row-(prev+1):
                if waslooped:
                    hasparam = False if noparam[col][1][beforeback] else True
                else:
                    if isinstance(noparam[col],list):
                        hasparam = False if noparam[col][0] else True
                    else:
                        hasparam = False if noparam[col] else True
                #==디버깅==
                #print(hasparam)
                if hasparam or (col != 0 and cnt[col-1] == 0 and loopback[col-1] == col-1 and isinstance(noparam[col-1],list) and noparam[col-1][0] == False):
                    pass
                elif string[start:i] != '':
                    if flag_1:
                        lendict[string][row] = None
                    elif flag_2:
                        lendict[string] = {row: None}
                    return None
                if isinstance(str_list[idx],list):
                    start=i
                    i+= idx_len
                    if string[start:i] in [' '+lr for lr in argleft+ argright]  and col+1 == len(parsed):
                        # 이건 ' '+argleft나 ' '+argright가 마지막 분리기호인 경우 괄호 쌍을 맞추기 위함이다.
                        # 이를 사용하는 변환은 삼각함수, 로그함수 등이 있다.
                        #print("Triangle Or Log  In Getlen")
                        i-= len(string[start:i]) - len(' ')
                        idx_len -= len(string[start:i]) - len(' ')
                else:
                    i+= idx_len
                #     i+=1
                # else:
                #     i += len(str_list[idx])
                start=i
                if loopback[col] is None:
                    col+=1
                    if col == len(parsed):
                        if flag_1:
                            lendict[string][row] = i
                        elif flag_2:
                            lendict[string] = {row: i}
                        return i
                    waslooped = False
                else:
                    cnt[col] += 1
                    beforeback = col
                    if times[col][1] == cnt[col]: # <1*1~2>에서 111을 11과 1로 끊어보기 위함
                        col+=1
                        if col == len(parsed):
                            if flag_1:
                                lendict[string][row] = i
                            elif flag_2:
                                lendict[string] = {row: i}
                            return i
                    else:
                        col = loopback[col]
                        waslooped = True
            else:
                
                #==디버깅==
                #print(string[i:],str_list,row,prev,idx)
                idx = idx+(prev+1)
                ciridx = idx - 1 if idx > row else idx #circulated idx
                #재귀적 호출
                #print("Recursive")
                length = getlen(string[i:],parsed_list,ciridx,begin,end)
                #print("Get Length")
                if length is not None:
                    i+= length
                    prev = -1
                else:
                    prev = idx
                    if prev+1 == len(parsed_list)+1:
                        prev = -1
                        i+=1
        else:
            idx,idx_len = getidx(string[i:],parsed,begin,end)
            if idx is not None and col != idx:
                # == 중요 ==
                if col > idx:
                    if flag_1:
                        lendict[string][row] = None
                    elif flag_2:
                        lendict[string] = {row: None}
                    return None
                if all(map(lambda x: getbool(x[0],x[1],begin,end),[[times[ii],cnt[ii]] for ii in range(col,idx+1)] )):
                    for ii in range(col,idx): #cnt[idx]는 초기화 안한다
                        cnt[ii] = 0
                    col =idx
                    waslooped = False
                elif all(map(lambda x: getbool(x[0],x[1],begin,end),[[times[ii],cnt[ii]] for ii in range(col,idx)] )):
                    for ii in range(col,idx):
                        cnt[ii] = 0
                    col = idx
                    waslooped= False
                else:
                    i+=1
                    prev = -1
                    #return None
            else:
                idx,idx_len = getidx(string[i:], [begin,end,'\\'+begin,'\\'+end,'\\\\','\\'],begin,end)
                prev = -1
                if idx is None:
                    i+=1
                elif idx == 0:
                    #==비긴엔드==
                    i+=len(begin)
                    # length = getlen(string[i:], begin_end_parsed,idx,begin,end)
                    # if length is not None:
                    #    i+= length
                    # else:
                    #    raise MyException("Begin '"+begin+"' And End '"+end+"' Not Matched")    
                elif idx==1:
                    i+=len(end)
                    
                    # raise MyException("End '"+end+"' Cant Be Used Alone")
                elif idx==5:
                    i+=1
                    #raise MyException("'\\' Must Be '\\\\'")
                else: # [2,5) -> 2,3,4
                    i+= len([begin,end,'\\'+begin,'\\'+end,'\\\\','\\'][idx])
    if loopback[col] is not None and getbool(times[col],cnt[col],begin,end) and col+1 == len(parsed):
        if waslooped:
            hasparam = False if noparam[col][1][beforeback] else True
        else:
            if isinstance(noparam[col],list):
                hasparam = False if noparam[col][0] else True
            else:
                hasparam = False if noparam[col] else True
        if hasparam is False:
            if flag_1:
                lendict[string][row] = start
            elif flag_2:
                lendict[string] = {row: start}
            return start
        if flag_1:
            lendict[string][row] = str_len
        elif flag_2:
            lendict[string] = {row: str_len}
        return str_len
    if flag_1:
        lendict[string][row] = None
    elif flag_2:
        lendict[string] = {row: None}
    return None
def repairparam(param_list, loopback, startidx, firstback, lastinsertidx, col):
    ii = startidx[col]
    if ii is None:
        #print("wasNone")
        ii = lastinsertidx
    
    #==디버깅==
    #print("received:",param_list,ii,lastinsertidx,col,loopback[col],firstback[col])
    if firstback[col]:
        param_list.insert(ii,param_list[ii:])
        #==디버깅==
        #print("fixed:",param_list[:ii+1])
        return param_list[:ii+1]
    else:
        param_list[ii] = param_list[ii]+param_list[ii+1:]
        #==디버깅==
        #print("fixed:",param_list[:ii+1])
        return param_list[:ii+1]

def getparam_list(string, parsed_list,row, begin,end):
    parsed = [i[0] for i in parsed_list[row]]
    loopback = [i[1] for i in parsed_list[row]]
    noparam = [i[2] for i in parsed_list[row]]
    times = [i[3] for i in parsed_list[row]]
    loopback_len = len(loopback)
    cnt = [0 for i in range(loopback_len)]
    lastinsertidx = 0
    insertidx = [None for i in range(loopback_len)]
    firstback = [True for i in range(loopback_len)]
    startidx = [None for i in range(loopback_len)]
    beforeback = None
    wasjumped = False
    lastlength = None
    jumprange = range(0)
    param_list = []
    start=0
    i= 0
    col = 0
    prev = -1
    str_len = len(string)
    waslooped = False
    #== 루프시작 ==
    while i < str_len:
        str_list = [parsed_list[i][0][0]  for i in range(len(parsed_list))]
        str_list.insert(row,parsed[col])
        str_list = str_list[prev+1:]
        # if col!= 0 and parsed[col-1][-len(argleft):] == argleft  and parsed[col][:len(argright)] == argright:
        #     idx = findpair_escaped(string[i-len(argleft):],argleft,argright)
        #     #     print("argrrrrr1:",string[i-len(argleft) +idx - len(argright):i-len(argleft)+idx - len(argright)+len(parsed[col])])
        #     #     print('parsed[col]',parsed[col])

        #     if idx is not None and string[i-len(argleft) +idx - len(argright):i-len(argleft)+idx - len(argright)+len(parsed[col])] == parsed[col]:
        #         i = i-len(argleft) +idx - len(argright)
        #         idx = row-(prev+1) 
        #         idx_len = len(parsed[col])
        #     else:
        #         #argleft, right들은 떨어질 수 없다 이말이야
        #         return lastlength
        # else:
        idx,idx_len = getidx(string[i:],str_list)
        #== 디버깅 쵝오
        
       # print(string[i:],param_list,str_list[idx] if idx is not None else  str_list, None if idx is None else idx+prev+1, row)
        # 1 & 2 & 3 \\\\ 
        if idx is not None:
            if idx+(prev+1) == row:    
                if waslooped:
                    hasparam = False if noparam[col][1][beforeback] else True
                else:
                    if isinstance(noparam[col],list):
                        hasparam = False if noparam[col][0] else True
                    else:
                        hasparam = False if noparam[col] else True
                #==디버깅==
                #print(noparam, noparam[col],beforeback,hasparam)
                if insertidx[col] is None:
                    lastinsertidx = insertidx[col] =  len(param_list)
                if hasparam or (col != 0 and cnt[col-1] == 0 and loopback[col-1] == col-1 and isinstance(noparam[col-1],list) and noparam[col-1][0] == False):
                    #궁극의 예외처리...  [[' +', ' -'], 2, [False, {2: False}], [0, 1]], [' } (', None, True, None]에서
                    # +, -가 안나왔을 때는 } (가 인자를 넣는 것을 허용하는 것 
                    #주의할점은 loopback이 자기자신이여야한다.
#                    if string[start:i] != '':
                    param_list.append(string[start:i])
                elif string[start:i] != '':
                    
                    if loopback[col] is not None and getbool(times[col],cnt[col],begin,end) and col+1 == len(parsed):
                        return (param_list,start)
                    return lastlength
                if wasjumped:
                    #==디버깅==
                    #print("firstback: ", firstback)
                    for ii in jumprange:
                        if startidx[ii] is None:
                            startidx[ii] = insertidx[loopback[ii]]
                        param_list = repairparam(param_list,loopback,startidx,firstback,lastinsertidx,ii)
                        
                if isinstance(str_list[idx],list):
                    start=i
                    i+=idx_len
                    if string[start:i] in [' '+lr for lr in argleft+ argright]  and col+1 == len(parsed):
                        # 이건 ' '+argleft나 ' '+argright가 마지막 분리기호인 경우 괄호 쌍을 맞추기 위함이다.
                        # 이를 사용하는 변환은 삼각함수, 로그함수 등이 있다.
                        #print("Triangle Or Log In Getparam")
                        i-= len(string[start:i]) - len(' ')
                        idx_len -= len(string[start:i]) - len(' ')
                    param_list.append(string[start:i])
                else:
                    i += idx_len
                start=i

                
                if loopback[col] is None:
                    col+=1
                    if col == len(parsed):
                        return (param_list,i) 
                    waslooped = False
                else:
                    cnt[col] += 1
                    beforeback = col
                    if startidx[col] is None:
                        #print("renew")
                        startidx[col] = insertidx[loopback[col]]
                    param_list = repairparam(param_list,loopback,startidx,firstback,lastinsertidx,col)
                    firstback[col] = False
                    #print(times[col][1], cnt[col])
                    if times[col][1] == cnt[col]:  # <1*1~2>에서 111을 11과 1로 끊어보기 위함
                        col+=1
                        if col == len(parsed):
                            return (param_list,i) 
                    else:
                        col = loopback[col]
                        waslooped = True
                if wasjumped:
                    for ii in jumprange:
                        insertidx[loopback[ii]] = None
                        startidx[ii] = None
                        firstback[ii] = True
                wasjumped = False
            else:
                #==디버깅==
                #print(string[i:],str_list,row,prev,idx)
                idx = idx+(prev+1)
                ciridx = idx - 1 if idx > row else idx #circulated idx
                length = getlen(string[i:],parsed_list,ciridx,begin,end)
                if length is not None:
                    i+= length
                    prev = -1
                else:
                    prev = idx
                    if prev+1 == len(parsed_list)+1:
                        prev = -1
                        i+=1
        else:
            idx ,idx_len= getidx(string[i:],parsed[col:])
            if idx is not None:
                idx+=col
            #==디버깅==
            #print(string[i:],parsed,col,idx)
            if idx is not None and col != idx:
                # == 중요 ==
                #print([[times[i],cnt[i]] for i in range(col,idx+1)])
                if col > idx:
                    return lastlength
                if all(map(lambda x: getbool(x[0],x[1],begin,end),[[times[ii],cnt[ii]] for ii in range(col,idx+1)] )):
                    for ii in range(col,idx): #cnt[idx]는 초기화 안한다
                        cnt[ii] = 0
                    jumprange = range(col,idx) 
                    wasjumped = True
                    waslooped = False
                    col = idx
                elif all(map(lambda x: getbool(x[0],x[1],begin,end),[[times[ii],cnt[ii]] for ii in range(col,idx)] )):
                    for ii in range(col,idx): #cnt[idx]는 초기화 안한다
                        cnt[ii] = 0
                    jumprange = range(col,idx) 
                    wasjumped = True
                    waslooped = False
                    col = idx
                else:
                    prev = -1
                    i+=1
                    #return None
            else:
                prev = -1
                idx,idx_len = getidx(string[i:], [begin,end,'\\'+begin,'\\'+end,'\\\\','\\'])
                if idx is None:
                    i+=1
                elif idx == 0:
                    i+= len(begin)
                   #==비긴엔드==
                    # length = getlen(string[i:], begin_end_parsed,idx,begin,end)
                    # if length is not None:
                    #     if i==0:
                    #         lastlength = length
                    #     i+= length
                    # else:
                    #     raise MyException("Begin '"+begin+"' And End '"+end+"' Not Matched")    
                elif idx==1:
                    i+= len(end)
                    #raise MyException("End '"+end+"' Cant Be Used Alone")
                elif idx==5:
                    i+=1
                    #raise MyException("'\\' Must Be '\\\\'")
                else: # [2,5) -> 2,3,4
                    i+= len([begin,end,'\\'+begin,'\\'+end,'\\\\','\\'][idx])
    if loopback[col] is not None and getbool(times[col],cnt[col],begin,end) and col+1 == len(parsed): #원래 cnt[col]+1이였음
        if waslooped:
            hasparam = False if noparam[col][1][beforeback] else True
        else:
            if isinstance(noparam[col],list):
                hasparam = False if noparam[col][0] else True
            else:
                hasparam = False if noparam[col] else True
        if hasparam is False:
            return (param_list,start)
        if string[start:] != '':
            if insertidx[col] is None:
                lastinsertidx = insertidx[col] =  len(param_list)
            param_list.append(string[start:])
        if startidx[col] is None:
            startidx[col] = insertidx[loopback[col]]
        #print(param_list,lastinsertidx)
        param_list = repairparam(param_list,loopback,startidx,firstback,lastinsertidx,col)
        return (param_list,i)
    return lastlength


def escape(string,esc_list,stay=[]):
    i=0
    str_len = len(string)
    str_list = ['\\'+esc for esc in esc_list]+['\\\\','\\']
    str_list_len = len(str_list)
    while i < str_len:
        idx= getidx(string[i:],str_list)[0]
        #==디버깅==
        #print(string[i:],str_list,idx)
        if idx is None:
            i+=1
        elif str_list_len-idx==1:
            i+=1
            #raise MyException("'\\' Must Be '\\\\'")
        elif str_list_len-idx==2:
            i+= len('\\\\')
        else:
            if idx in stay:
                i+=len(str_list[idx])
            else:
                return string[:i] + esc_list[idx] + escape(string[i+len(str_list[idx]):],esc_list)
    return string


def find_escaped(string, target,begin='',end='',esc=''):
    i=0
    if esc=='':
        esc= target
    str_len = len(string)
    if begin=='' and end == '':
        while i < str_len:
            idx = getidx(string[i:],[target,'\\'+esc])[0]
            if idx==0:
                return i
            elif idx==1:
                i+= len('\\'+esc)
            else:
                i+=1
    else:
        while i < str_len:
            idx= getidx(string[i:],[target,begin,end,'\\'+esc,'\\'+begin,'\\'+end,'\\\\','\\'])[0]
            #== 디버깅 ==
            #print(string[i:], idx)
            if idx is None:
                i+=1
            elif idx==0:
                return i
            elif idx==1:
                #==비긴엔드==
                #i+=len(begin)
                i+= getlen(string[i:],begin_end_parsed,0,begin,end)
            elif idx==2:
                #i+=len(end)
                raise MyException("End '"+end+"' Cant Be Used Alone")
            elif idx==7:
                i+=1
                #raise MyException("'\\' Must Be '\\\\'")
            else:
                i+=len([target,begin,end,'\\'+esc,'\\'+begin,'\\'+end,'\\\\','\\'][idx])      
    return None

def getcode(string,begin,end,esc=''):
    """
    :return: 문자 코드를 리턴, 문자 코드를 얻을 수 없는 경우 return None
    """
    code = -1
    str_len = len(string)
    i=0
    if str_len ==0:
        return code
    elif str_len == 1:
        if string == begin or string == end or string == esc:
            return None
        return ord(string)
    elif string[:2] == '\\x':
        try:
            code = int(string[2:],16)
            return code
        except:
            return None
    else:
        esc_list = ['\\'+begin,'\\'+end]
        if esc != '':
            esc_list.insert(0,'\\'+esc)
        idx= getidx(string,esc_list)[0]
        if idx is None:
            return None
        else:
            code = ord(esc_list[idx][1:])
            return code        
        
def split_escaped(string, pivot):
    idx = find_escaped(string, pivot)
    if idx is None:
        return [string]
    return [string[:idx]] + split_escaped(string[idx+len(pivot):],pivot)

def getbool(times,x,begin,end):
    #==디버깅==
    #print(times,x,begin,end)
    """
    :times: times는 정수만 가지는 리스트여야 한다. 
    """
    #==비긴엔드==
    # x= begin if x== '\\'+begin else x
    # x = end if x=='\\'+end else x
    if isinstance(x,str):
        x= ord(x[0])
    if times is None:
        return False
    elif len(times) == 0:
        return True
    elif len(times) == 1:
        return x==times[0]
    elif len(times) == 2:
        return (True if times[0] == -1 else x>=times[0])  and  (True if times[1] == -1 else x<=times[1])
    else:
        raise MyException("Times Size Must Be Less Than 3")        

#== 중요==
# <시작문자 - 끝문자> [* 최소횟수 ~ 최대횟수]>
# 해당 범위 탐색
# <>
# <, > 안에 있고, ', ' 안에 없는 param문자열 -> 만능 문자
# <문자열*횟수1~횟수2>
# 횟수1 이상 횟수 2 이하 번 반복되는 문자열
# 횟수1 = 횟수 2인경우 횟수1만 적어도 됨
# 구간이 무한집합인 경우 횟수1, 횟수2를 안적고 ~만 적으면 됨

# == 중요 ==
# parse의 첫 호출 시 wasparam은 None이고 flag를 True로 지정한다.
# wasparam은 param 문자열을 만나면 True가 된다
# 널문자로 문자열을 append한 경우('' 제외) False가 된다.
# 재귀 호출 시 wasparam이 None이면 False를 그렇지 않으면 wasparam을 넘겨준다.
# 
# 몇 가지 경우에서는 빈문자열 슬라이싱은 오류를 발생시킨다
# 1. wasparam이 True인 경우
# 2. wasparam이 None인 경우
# 3. 구분문자인 경우
# 4. 널문자에 의해 잘렸으면 flag가 True인 경우에 오류가 발생(wasparam는 상관 없음)
# 4-1. end와 널문자 사이의 슬라이싱인 경우에는 절대 오류를 발생시키지 않는다.
# 
# 아래 몇가지 경우에서는 이전 문자열과 현재 문자열 사이에 인자가 없다.
# 1. wasparam이 False이거나 None 경우 (True가 아닌 경우)
# 1-1. 널문자에 의해 잘렸으면 wasparam이 None인 경우는 제외 (False인 경우)
# 2. 정말 특수한 경우인데 평소에는 True이다가 loopback에 의해 돌아온 경우 False이다.
# 2-1. 그 반대 경우로 평소에는 False이다가 loopback에 의해 돌아온 경우 True일 수도 있다.
# 
# ... 있으면 list형
# ... 없으면
#   split_escaped(-)의 len이 2이고
#   getcode[0], getcode[1]이 None이 아니면 범위형
#   만능 문자는 <->로 씀
#   \x+숫자(1~4자리) 형태면 코드형
#   남은 건 *[~]반복형
def findpair_escaped(string, left,right):
    
    i=0
    str_len = len(string)
    left_len = len(left)
    right_len = len(right)
    left_right =0
    if string[:left_len] != left:
        raise MyException("Left '"+left+"' Must Be First Of String '"+string+"'")
    while i< str_len:
        idx = getidx(string[i:],[left,right,'\\\\'])[0]
        if idx is None:
            i+=1
        elif idx == 0:
            left_right+=1
            i+= left_len
        elif idx == 1:
            left_right -=1
            i+= right_len
        elif idx==2:
            i+= len('\\\\')
        if left==right and left_right == 2:
            return i
        elif left_right == 0:
            return i
    return None

def getpattern(string, begin,end):
    """
    :return: 0: ''..., 1: -, 2: <*[~]>, 3: 그외
    """
    # 2는 \... 3은 \*, \...의 이스케이프가 필요함
    begin_len = len(begin)
    end_len = len(end)
    length = getlen(string,begin_end_parsed,0,begin,end)
    #==디버깅==
    #print(string,begin,end,length)
    if length is None:
        raise MyException("Begin '"+begin+"' And End '"+end+"' Not Matched")  
    else:
        try:
            find_escaped(string[begin_len:],'...',begin,end)
            return 0
        except:
            pass
        try:
            splited = split_escaped(string[begin_len:length-end_len],'-')
            if len(splited) == 2 and getcode(splited[0],begin,end,'-') is not None and getcode(splited[1],begin,end) is not None:
                return 1
        except:
            pass    
        try:
            find_escaped(string[begin_len:],'*',begin,end)
            return 2
        except:
            pass
    return 3

def pair_replace(string, left, right, new_left, new_right,begin,end):
    """
    :param string: left,right를 포함하고 있는 문자열
    :param left: '(' 같이 right와 짝을 이루는 문자열
    :param right: ')' 같이 left와 짝을 이루는 문자열
    :param new_left: '{' 같이 new_right와 짝을 이루고 left와 교체될 문자열 
    :param new_right: '}' 같이 new_left와 짝을 이루고 right와 교체될 문자열
    :param begin: '\\[' 같이 end와 짝을 이루는 문자열
    :param end: '\\] 같이 begin과 짝을 이루는 문자열
    :param begin_end: begin과 end사이는 건너 뛸 지 여부
    :return: 오류 발생 시 MyExcepion Raise, 그 이외에는 left를 new_left로 right를 new_right로 교체한 문자열을 반환한다.
    """
    #========================
    left_len = len(left)
    right_len = len(right)
    str_len = len(string)
    i=0
    #================
    while i< str_len:
        idx= getidx(string[i:],[left,'\\'+begin,'\\'+end,'\\\\','\\'])[0]
        if idx is None:
            i+=1
        elif idx==0:
            idx = findpair_escaped(string[i:], left,right)
            if idx is  None:
                raise MyException("Left '"+left+"' And Right '"+right+"' Not Matched")    
            return string[:i] + new_left +\
            pair_replace(string[i+left_len:i+idx-right_len],left,right,new_left,new_right,begin,end) +\
            new_right + pair_replace(string[i+idx:],left,right,new_left,new_right,begin,end) 
        elif idx<=3:
            i+= len([left,'\\'+begin,'\\'+end,'\\\\','\\'])
        elif idx==4:
            i+=1
            #raise MyException("'\\' Must Be '\\\\'")
    return string

        
def replace_escaped(string, esc_list,new_list):
    
    i=0
    str_len = len(string)
    while i< str_len:
        idx = getidx(string[i:],esc_list)[0]
        #==디버깅==
        if idx  is not None:
            return string[:i] + new_list[idx] + replace_escaped(string[i+len(esc_list[idx]):],esc_list,new_list)
        i+=1
    return string
def parse(string,param,parsed,wasparam, begin, end):
    #=====

    flag= True if wasparam is None else False
    str_list = [begin, '\'', '\'', '...', end]
    str_list2 = [begin, '*', '~', end]
    #== 디버깅 ==
    #print("called :",string,wasparam)
    str_len = len(string)
    param_len = len(param)
    i = 0
    start = 0
    #=====
    while i < str_len:
        idx = getidx(string[i:], [param, begin, end, '\\' +param, '\\'+begin, '\\'+end, '\\\\', '\\'])[0]
        if idx is None:
            i += 1
        else:
            if idx == 0:
                if string[start:i] == '':
                    if wasparam is not False:
                        raise MyException("Empty('') Cant Be In Splited")
                else:
                    escaped_str = escape(string[start:i],[param,begin,end,'\\'])
                    parsed.append([escaped_str,None,True if wasparam is not True else False,None ])    
                wasparam=True
                i += param_len
                start = i
            elif idx==1:
                pattern = getpattern(string[i:],begin,end)
                length = getlen(string[i:],begin_end_parsed,0,begin,end)
                #==디버깅==
                #print(string[i:],length,pattern,parsed,wasparam)
                if pattern == 0:
                    loopback = len(parsed) 
                    start_str = ''
                    for j in range(len(str_list)):
                        idx = find_escaped(string[i:],str_list[j],begin,end, '.' if j==3 else '')
                        #==디버깅==
                        #print(parsed,string[i:],idx)
                        if idx is None:
                            raise MyException("'"+string+"' Cant Be Parsed")
                        else:   
                            i += idx
                            #==이스케이프
                            #얘는 Stay해야함
                            escaped_str = escape(string[start:i],['.' if j==3 else str_list[j],begin,end],stay=[1,2]) 
                            if escaped_str == '':
                                if j==2 or j==3:
                                    raise MyException("Empty('') Cant Be In Splited")
                            else:
                                if j<=1: # begin 이전과 시작문자
                                    parsed, wasparam = parse(escaped_str,param,parsed,False if wasparam is None else wasparam,begin,end)          
                                    loopback = len(parsed)
                                    
                                elif j==3: # 구분 문자 부분
                                    parsed, wasparam = parse(escaped_str,param,parsed, False if wasparam is None else wasparam,begin,end)
                                    parsed[-1][1] = loopback
                                    parsed[-1][3] = [0,-1]#times
                                    usual = loopback #평소

                                    #시작 - 구분 - 시작이 부적합한지 검사
                                    byloop = len(parsed) #loopback에 의해 돌아왔을 때   
                                    #==디버깅 == 
                                    #print(usual,byloop)
                                    parsed, wasparam = parse(start_str,param,parsed, False if wasparam is None else wasparam,begin,end)
                                    sliceflag = False
                                    if len(parsed) <= byloop:
                                        byloop = usual
                                    else:
                                        sliceflag = True
                                        byloop -= 1
                                    if isinstance(parsed[usual][2],list):
                                        parsed[usual][2][1][byloop] = parsed[byloop][2]
                                    else:
                                        parsed[usual][2] = [parsed[usual][2], {byloop: parsed[byloop][2]}]
                                    if sliceflag:
                                        parsed=parsed[:byloop+1]
                                else:
                                    if j==2:
                                        start_str = escaped_str
                                    parsed, wasparam = parse(escaped_str,param,parsed,False if wasparam is None else wasparam,begin,end)
                            i += len(str_list[j])
                            start = i
                    if string[start:] =='':
                        return parsed, wasparam  
                elif pattern == 1:
                    #==이스케이프
                    #얘는 Stay해야함
                    escaped_str = escape(string[start:i],[begin,end],stay=[0,1]) 
                    if escaped_str != '':
                        parsed, wasparam = parse(escaped_str,param,parsed,False if wasparam is None else wasparam,begin,end)  
                    #==이스케이프
                    escaped_str = escape(string[i+len(begin):i+length-len(end)], [begin,end] )
                    splited = split_escaped(escaped_str,'-')
                    parsed.append([[getcode(splited[0],begin,end,'-'),getcode(splited[1],begin,end)],None,True if wasparam is not True else False,None])
                    i+= length
                    start=i
                    wasparam = False
                    if string[start:] =='':
                        return parsed, wasparam
                    #print(parsed)
#============================== 패턴 2===============================
                elif pattern == 2:
                    loopback = len(parsed) 
                    start_str = ''
                    times = []
                    for j in range(len(str_list2)):
                        try:
                            idx = find_escaped(string[i:],str_list2[j],begin,end)
                        except:
                            idx = None
                        #print(string[i:],idx)
                        
                        if idx is None:
                            if j==2:# ~만 없을 수 있다.
                                pass
                            else:
                                raise MyException("'"+string+"' Cant Be Parsed")
                        else:   
                            i += idx
                            #==이스케이프==
                            escaped_str = escape(string[start:i],['...',str_list2[j],begin,end],stay=[1,2])
                            if j==3: # 최대횟수
                                if escaped_str == '':
                                    times.append(-1)
                                else:
                                    try:
                                        times.append(int(escaped_str))
                                    except:
                                        raise MyException("Maximum Times Must Be Int")
                                if len(times) == 1 and times[0] <= 1:
                                    raise MyException("You Cant Use *0 Or *1")    
                                parsed[-1][1] = loopback
                                parsed[-1][3]  = times

                                #시작 - 구분 - 시작이 부적합한지 검사
                                usual = loopback #평소
                                #print(parsed,wasparam,usual,loopback)
                                byloop = len(parsed) #loopback에 의해 돌아왔을 때   
                                parsed, wasparam = parse(start_str,param,parsed, False if wasparam is None else wasparam,begin,end)
                                
                                #==디버깅 == 
                                #print(parsed,wasparam,usual,loopback)
                                sliceflag = False
                                if len(parsed) <= byloop:
                                    byloop = usual
                                else:
                                    sliceflag = True
                                    byloop -= 1
                                if isinstance(parsed[usual][2],list):
                                    parsed[usual][2][1][byloop] = parsed[byloop][2]
                                else:
                                    parsed[usual][2] = [parsed[usual][2], {byloop: parsed[byloop][2]}]
                                if sliceflag:
                                    parsed=parsed[:byloop+1]
                            elif escaped_str == '':
                                if j==1:
                                    raise MyException("Empty('') Cant Be In Splited")
                                elif j==2:                                    
                                    raise MyException("Minimum Times Cant Be Empty('')")
                            else:
                                if j==0: #begin 이전
                                    parsed, wasparam = parse(escaped_str,param,parsed,False if wasparam is None else wasparam,begin,end)          
                                    loopback = len(parsed)
                                elif j==1: #반복할문자열
                                    start_str= escaped_str
                                    parsed, wasparam = parse(escaped_str,param,parsed,False if wasparam is None else wasparam,begin,end) 
                                    
                                elif j==2:
                                    try:
                                        times.append(int(escaped_str))
                                    except:
                                        raise MyException("Minimum Times Must Be Int")
                            i += len(str_list2[j])
                            start = i
                    if string[start:] =='':
                        return parsed, wasparam 
                elif pattern == 3:
                    #==이스케이프
                    #얘는 Stay해야함
                    escaped_str = escape(string[start:i],[begin,end],stay=[0,1]) 
                    if escaped_str != '':
                        parsed, wasparam = parse(escaped_str,param,parsed,False if wasparam is None else wasparam,begin,end)  
                    #==이스케이프==
                    escaped_str = escape(string[i+len(begin):i+length-len(end)],['...','*',begin,end])
                    splited = split_escaped(escaped_str,'|')
                    splited = list(map(lambda x : escape(x,'|'),splited))
                    #print([splited, None, True if wasparam is not True else False,None ])
                    parsed.append([splited, None, True if wasparam is not True else False,None ])    
                    i+=length
                    start =i
                    wasparam = False
                    if string[start:] =='':
                        return parsed, wasparam
                    
            elif idx==2:
                raise MyException("End '"+end+"' Cant Be Used Alone")
            elif idx==7:
                i+=1
                #raise MyException("'\\' Must Be '\\\\'")
            else: # [3,7) -> 3,4,5,6
                i+= len([param,begin,end,'\\'+param,'\\'+begin,'\\'+end,'\\\\','\\'][idx])
    
    if string[start:] == '':
        if flag:
            raise MyException("Empty('') Cant Be In Splited")
    else:
        #==디버깅==
        #print("Cut By Null :", string[start:])
        parsed.append([string[start:],None,True if wasparam is not True else False,None])
        wasparam = False
    return parsed, wasparam
        
def print_parse(string,param,parsed,wasparam, begin, end):
    try:
        print(parse(string,param,parsed,wasparam,begin,end)[0])    
    except MyException as e:
        print(e.msg)
#대애충 convert는 len(parsed_list)만큼 for돌면서 getparam_list(,row)해서 None이면 continue, None이 아니면 param_list = map(lambda x : convert,param_list)  후
#
maximum_call = 2
img2latex_call = 0
def img2latex(filename):
    global maximum_call, img2latex_call
    # put desired file path here
    if maximum_call == img2latex_call:
        raise MyException("Dont Call img2latex More Than "+str(maximum_call))
    img2latex_call+=1
    file_path = filename
    image_uri = "data:image/jpg;base64," + str(base64.b64encode(open(file_path, "rb").read()))[2:-1]
    r = requests.post("https://api.mathpix.com/v3/latex",
        data=json.dumps({'src': image_uri, 'ocr' : ['math','text']}),
        headers={"app_id": "msjang4_dgsw_hs_kr", "app_key": "caacac60603c51823275", 
                "Content-type": "application/json"})
    print(json.dumps(json.loads(r.text), indent=4, sort_keys=True))
    return json.loads(r.text)['latex']
def center_align_img(img,size):
    img.thumbnail((50,50), Image.ANTIALIAS)
    layer = Image.new('RGB', size, (255,255,255))
    layer.paste(img, tuple(map(lambda x: (x[0]-x[1])//2, zip(size, img.size))))
    return layer
def latex2img(latex,x=0.001, y=0.001,size=30,imgsize=None,filename='output.png'):
    
    fig = plt.figure()
    plt.text(x, y, r"$%s$" % latex, fontsize = size)
    fig.patch.set_facecolor('white')
    plt.axis('off')
    plt.tight_layout()

    with io.BytesIO() as png_buf:
        plt.savefig(png_buf, bbox_inches='tight', pad_inches=0)
        png_buf.seek(0)
        image = Image.open(png_buf)
        image.load()
        inverted_image = ImageOps.invert(image.convert("RGB"))
        cropped = image.crop(inverted_image.getbbox())
        if imgsize is not None:
            cropped = center_align_img(cropped,imgsize)
        cropped.save(filename)
    plt.close(fig)
    
def convertall(string,parsed_list,form_list,eval_list,begin,end):
    parsed_list_len = len(parsed_list)
    for row in range(parsed_list_len):
        string = convert(string,parsed_list,form_list,eval_list,begin,end,row)
        #==디버깅 쵝오
        
        #print(row,": ",repr(string))
    return string

def convert(string,parsed_list,form_list,eval_list,begin,end,row):
    #==디버깅==
    #print(string)
    doeval = eval_list[row]
    str_len = len(string)
    if isinstance(string, list):
        str_list = []
        for i in range(str_len):
            str_list.append(convert(string[i],parsed_list,form_list,eval_list,begin,end,row))
        return str_list
    i=0
    while i< str_len:
        param_list = getparam_list(string[i:],parsed_list,row,begin,end)
        #==디버깅==
        #print("debug: ",string[i:],"list: ",param_list)
        if param_list is not None:
            if isinstance(param_list,int):
                i+=param_list
            else:
                #print( "len: ",len(param_list[0]))
                length = param_list[1]
                param_list = param_list[0]
                #print(param_list,string,doeval)
                if len(param_list) ==1 and isinstance(param_list,list) and len(param_list[0]) ==1 and param_list[0][0] == string:
                    #=무한 재귀 방지
                    return string
                    # if doeval:
                    #     return eval(form_list[row].format(*param_list))            
                    # else:
                    #     return form_list[row].format(*param_list)
                param_list = convert(param_list,parsed_list,form_list,eval_list,begin,end,row)
                if doeval:
                    return string[:i] + eval(form_list[row].format(*param_list)) + convert(string[i+length:],parsed_list,form_list,eval_list,begin,end,row)

                else:
                    return string[:i] + form_list[row].format(*param_list) + convert(string[i+length:],parsed_list,form_list,eval_list,begin,end,row)
        else:
            i+=1
    return string
begin_end_parsed=[]

def wannaconvert(wanna,symbs):
    #=디버깅
    symbs = symbs + [relationals]+[argleft]+[argright]+[reduce(operator.add,symbs)] 
    #print("Receive: ", wanna)
    str_list = ['Complex','Matrix','Function','Relational','Argleft','ArgRight','All']
    for i in range(len(str_list)):
        wanna =wanna.replace('{'+str_list[i]+'}','<'+'|'.join(symbs[i])+'>')
    for i in range(len(str_list)):
        wanna= wanna.replace('{'+' '+str_list[i]+'}','<'+'|'.join([' '+symbol for symbol in symbs[i]])+'>')
    for i in range(len(str_list)):
        wanna= wanna.replace('{'+str_list[i]+' '+'}','<'+'|'.join([symbol+' ' for symbol in symbs[i]])+'>')
    for i in range(len(str_list)):
        wanna= wanna.replace('{'+' '+str_list[i]+' '+'}','<'+'|'.join([' '+symbol+' ' for symbol in symbs[i]])+'>')
    for i in range(len(str_list)):
        if i==3:
            continue
        wanna=wanna.replace('{'+'-'+str_list[i]+'}','<'+'|'.join(reduce(operator.add,symbs[:i]+symbs[i+1:3]))+'>')
    

    #=디버깅
    #print("Converted : ",wanna)
    return wanna

primitive = (int, str, bool, float)
def interpret(sympyform, func = 0):
    #print('sympyform : ',sympyform)
    exec('eqr = '+sympyform,globals())
    if type(eqr) in primitive:
        print("is_Primitive")
        answer = latex(eqr)
    elif eqr.is_Relational:
        print("is_Relational ",end='')
        if func== 0: #선형방정식
            print("linear")
            answer = latex(solve(eqr,dict=True))
        elif func == 1: #미분방정식
            print("derivative")
            answer = latex(dsolve(eqr))
        elif func == 2: #집합연산
            print("set")
            answer = latex(solveset(eqr))
    else:
        if func == 3: #인수분해
            print("factor")
            answer = latex(factor(eqr))
        elif func == 4: #전개
            print("expand")
            answer = latex(expand(eqr))
        else:
            print("is_Nothing")
            answer = eqr

    return answer
argleft=['{','[','(']
argright=['}',']',')']
def init(begin,end,filename,symbs):
    global begin_end_parsed
    begin_end_parsed = [[[begin,None,True,None],[end,None,False,None]]]
    f = open(filename,'r',encoding='utf-8') 
    exec(','.join(symbs[0]) + '='+ 'symbols(\''+' '.join(symbs[0])+'\')',globals())
    exec(','.join(symbs[2]) + '='+ 'symbols(\''+' '.join(symbs[2])+'\',cls=Function)',globals())
    symbs[2] = symbs[2] + defaultfunction
    parsed_list = []
    form_list = []
    eval_list = []
    lines = f.readlines()
    if len(lines) % 7 != 0:
        # docs ,doeval , param , wanna, left, right, form 총 6부분으로 이루어져있다.
        raise MyException("Number Of Lines Not Multiples Of 7")
    for idx in range(0,len(lines),7):
        idx+=1
        doeval = True if lines[idx][:-1] == 'True' else False
        eval_list.append(doeval)
        param = lines[idx+1][:-1]
        wanna = lines[idx+2][:-1]
        wanna = wannaconvert(wanna,symbs)
        parsed = parse(wanna,param,[],None,begin,end)[0]
        #left = replace_escaped(lines[idx+3][:-1],['{','}'],['\\{','\\}'])
        #right = replace_escaped(lines[idx+4][:-1],['{','}'],['\\{','\\}'])
        left = lines[idx+3][:-1]
        right = lines[idx+4][:-1]
        form = pair_replace(replace_escaped(lines[idx+5][:-1],['\\{','\\}'],['{{','}}']),left,right,'{','}',begin,end)
        if doeval:
            form = form
        form_list.append(form)
        #print(form)
        parsed_list.append(parsed)
    return parsed_list, form_list,eval_list
if __name__ == '__main__':
    begin = '<'
    end = '>'
    parsed_list =[]
    form_list = []
    f = open("function.txt", 'r')
   #=============
    doeval = True if f.readline().strip() == 'True' else False
    param = f.readline().strip()
    wanna = f.readline().strip()
    parsed = parse(wanna,param,[],None,begin,end)[0]
    print(parsed)

    parsed_list.append(parsed)
    example = 'Matrix(2,3,[1,2,3,4,5,6])'
    param_list =getparam_list(example,parsed_list,0,begin,end)
    print(param_list)
    left = replace_escaped(f.readline().strip(),['{','}'],['\\{','\\}'])
    right = replace_escaped(f.readline().strip(),['{','}'],['\\{','\\}'])
    form = pair_replace(f.readline().strip(),left,right,'{','}',begin,end)
    form_list.append(form)
    print(doeval,param,wanna,left,right,form)

   #=======================

    doeval = True if f.readline().strip() == 'True' else False
    param = f.readline().strip()
    wanna = f.readline().strip()
    parsed = parse(wanna,param,[],None,begin,end)[0]
    print(parsed)

    parsed_list.append(parsed)
    example = 'a3d[[1,2,3],[4,5,6]]'
    param_list =getparam_list(example,parsed_list,1,begin,end)
    print(param_list)
    left = replace_escaped(f.readline().strip(),['{','}'],['\\{','\\}'])
    right = replace_escaped(f.readline().strip(),['{','}'],['\\{','\\}'])
    form = pair_replace(f.readline().strip(),left,right,'{','}',begin,end)
    form_list.append(form)
    print(doeval,param,wanna,left,right,form)

    #===================
    example = 'a3d[[]]'
    param_list =getparam_list(example,parsed_list,1,begin,end)
    print(param_list)
    #===============
    
    doeval = True if f.readline().strip() == 'True' else False
    param = f.readline().strip()
    wanna = f.readline().strip()
    parsed = parse(wanna,param,[],None,begin,end)[0]
    print(parsed)

    parsed_list.append(parsed)
    example = 'a3a'
    param_list =getparam_list(example,parsed_list,2,begin,end)
    print(param_list)
    left = replace_escaped(f.readline().strip(),['{','}'],['\\{','\\}'])
    right = replace_escaped(f.readline().strip(),['{','}'],['\\{','\\}'])
    form = pair_replace(f.readline().strip(),left,right,'{','}',begin,end)
    form_list.append(form)
    print(doeval,param,wanna,left,right,form)

    example = 'Matrix(a2a,b3b,[c1c,d2d,e3e,f4f,g5g,h6h])'
    #example = 'Matrix(2,3,[1,2,3,4,5,6])'

    print(getparam_list(example,parsed_list,0,begin,end))
    #print(convertall(example,parsed_list,form_list,begin,end))
    #print(eval(convert(example,parsed_list,form_list,begin,end)))
