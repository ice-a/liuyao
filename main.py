import time
import streamlit as st
import random
import json
from openai import OpenAI
import os

# 从 Docker 环境变量中获取 API 密钥和 base_url
deepseek_api_key = os.getenv('API_KEY')  # 从环境变量中读取 API 密钥
base_url = os.getenv('BASE_URL', "https://api.deepseek.com")  # 从环境变量中读取 base_url，默认值为 "https://api.deepseek.com"
model = os.getenv('MODEL', "deepseek-chat")
# 检查 API 密钥是否存在
if not deepseek_api_key:
    st.error("未找到环境变量 'DEEPSEEK_API_KEY'，请确保已正确设置。")
    st.stop()

# 初始化 OpenAI 客户端
client = OpenAI(api_key=deepseek_api_key, base_url=base_url)

# 卦象字典
gua_dict = {
    '阳阳阳': '乾',
    '阴阴阴': '坤',
    '阴阳阳': '兑',
    '阳阴阳': '震',
    '阳阳阴': '巽',
    '阴阳阴': '坎',
    '阳阴阴': '艮',
    '阴阴阳': '离'
}

# 爻位字典
number_dict = {
    0: '初爻',
    1: '二爻',
    2: '三爻',
    3: '四爻',
    4: '五爻',
    5: '六爻',
}

# 加载卦象描述文件
try:
    with open('gua.json', "r", encoding="utf-8") as gua_file:
        des_dict = json.load(gua_file)
except FileNotFoundError:
    st.error("未找到卦象描述文件 'gua.json'，请确保文件存在。")
    st.stop()
except json.JSONDecodeError:
    st.error("卦象描述文件 'gua.json' 格式错误，请检查文件内容。")
    st.stop()

# 设置页面配置
st.set_page_config(
    page_title="六爻游戏",
    page_icon="🔮",
    layout="centered",
)

# 页面标题和说明
st.markdown('## 六爻游戏')
st.markdown("""
六爻为丢 **六次** 三枚硬币，根据三枚硬币的正反（字背）对应本次阴阳，三次阴阳对应八卦中的一卦  
六次阴阳对应六爻，六爻组合成两个八卦，对应八八六十四卦中的卦辞，根据卦辞进行 **随机** 解读  

为保证可用性和成本限制，每次只能提问**一个问题**，请谨慎提问
""")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": [{"type": "text", "content": "告诉我你心中的疑问吧 ❤️"}]
    }]
if "disable_input" not in st.session_state:
    st.session_state.disable_input = False
if "history" not in st.session_state:
    st.session_state.history = []

# 显示历史记录
if st.session_state.history:
    with st.expander("查看历史记录"):
        for idx, record in enumerate(st.session_state.history):
            st.markdown(f"**记录 {idx + 1}**")
            st.markdown(f"问题: {record['question']}")
            st.markdown(f"卦象: {record['gua']}")
            st.markdown(f"解读: {record['interpretation']}")
            st.markdown("---")

# 显示聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for content in message["content"]:
            if content["type"] == "text":
                st.markdown(content["content"])
            elif content["type"] == "image":
                st.image(content["content"])
            elif content["type"] == "video":
                st.video(content["content"])


# 添加消息的函数
def add_message(role, content, delay=0.05):
    with st.chat_message(role):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in list(content):
            full_response += chunk + ""
            time.sleep(delay)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)


# 生成三枚硬币的结果
def get_3_coin():
    try:
        return [random.randint(0, 1) for _ in range(3)]
    except Exception as e:
        st.error(f"生成硬币结果时出错: {e}")
        return [0, 0, 0]  # 返回默认值


# 根据硬币结果判断阴阳
def get_yin_yang_for_coin_res(coin_result):
    return "阳" if sum(coin_result) > 1.5 else "阴"


# 格式化硬币结果
def format_coin_result(coin_result, i):
    return f"{number_dict[i]} 为 " + "".join(
        [f"{'背' if i > 0.5 else '字'}" for i in coin_result]) + " 为 " + get_yin_yang_for_coin_res(coin_result)


# 禁用输入
def disable():
    st.session_state["disable_input"] = True


# 用户输入问题
if question := st.chat_input(placeholder="输入你内心的疑问", key='input', disabled=st.session_state.disable_input,
                             on_submit=disable):
    if not question.strip():
        st.warning("问题不能为空，请输入你的疑问。")
        st.stop()

    add_message("user", question)

    # 生成首卦
    first_yin_yang = []
    for i in range(3):
        coin_res = get_3_coin()
        first_yin_yang.append(get_yin_yang_for_coin_res(coin_res))
        add_message("assistant", format_coin_result(coin_res, i))

    first_gua = gua_dict.get("".join(first_yin_yang), "未知")
    add_message("assistant", f"您的首卦为：{first_gua}")

    # 生成次卦
    second_yin_yang = []
    for i in range(3, 6):
        coin_res = get_3_coin()
        second_yin_yang.append(get_yin_yang_for_coin_res(coin_res))
        add_message("assistant", format_coin_result(coin_res, i))
    second_gua = gua_dict.get("".join(second_yin_yang), "未知")
    add_message("assistant", f"您的次卦为：{second_gua}")

    # 组合卦象
    gua = second_gua + first_gua
    gua_des = des_dict.get(gua, {"name": "未知", "des": "无描述", "sentence": "无卦辞"})
    add_message("assistant", f"""
        六爻结果: {gua}  
        卦名为：{gua_des['name']}   
        {gua_des['des']}   
        卦辞为：{gua_des['sentence']}   
    """)

    # 调用 API 进行解读
    with st.spinner('加载解读中，请稍等 ......'):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system",
                           "content": "你是一位出自中华六爻世家的卜卦专家，你的任务是根据卜卦者的问题和得到的卦象，为他们提供有益的建议。你的解答应基于卦象的理解，同时也要尽可能地展现出乐观和积极的态度，引导卜卦者朝着积极的方向发展。"},
                          {"role": "user", "content": f"""
                          问题是：{question},
                          六爻结果是：{gua},
                          卦名为：{gua_des['name']},
                          {gua_des['des']},
                          卦辞为：{gua_des['sentence']}"""}],
                stream=False)
            interpretation = response.choices[0].message.content
        except Exception as e:
            st.error(f"API 调用失败: {e}")
            interpretation = "无法生成解读，请稍后重试。"

    add_message("assistant", interpretation)
    time.sleep(0.1)

    # 保存到历史记录
    st.session_state.history.append({
        "question": question,
        "gua": gua,
        "interpretation": interpretation
    })
