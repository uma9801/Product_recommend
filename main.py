"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
from dotenv import load_dotenv
import logging
import streamlit as st
import utils
from initialize import initialize
import components as cn
import constants as ct
# javascript有効化のためのライブラリ
import streamlit.components.v1 as components
# スクロールナビゲーション用ライブラリ
#from streamlit_scroll_navigation import scroll_navbar

############################################################
# 設定関連
############################################################
st.set_page_config(
    page_title=ct.APP_NAME
)

load_dotenv()

logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 初期化処理
############################################################
try:
    initialize()
except Exception as e:
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE))
    st.stop()

# アプリ起動時のログ出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)


############################################################
# 初期表示
############################################################
# タイトル表示
cn.display_app_title()

# # scroll_navigation設定
# anchor_ids = ["Top", "answer", "bottom"]
# anchor_icons = ["arrow-bar-up", "chat-text", "arrow-bar-down"]

# # horizontal menu
# scroll_navbar(
#     anchor_ids,
#     anchor_icons=anchor_icons,
#     orientation="horizontal"
# )
# st.subheader(anchor_ids[0], anchor=anchor_ids[0])

# AIメッセージの初期表示
cn.display_initial_ai_message()


############################################################
# 会話ログの表示
############################################################
try:
    cn.display_conversation_log()
except Exception as e:
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE))
    st.stop()


############################################################
# チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 1. ユーザーメッセージの表示
    # ==========================================
    logger.info({"message": chat_message})

    # # スクロール用アンカーの設置
    # st.subheader(anchor_ids[1], anchor=anchor_ids[1])

    with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
        st.markdown(chat_message)

    # ==========================================
    # 2. LLMからの回答取得
    # ==========================================
    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            result = st.session_state.retriever.invoke(chat_message)
        except Exception as e:
            logger.error(f"{ct.RECOMMEND_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.RECOMMEND_ERROR_MESSAGE))
            st.stop()
    
    # ==========================================
    # 3. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        try:
            cn.display_product(result)
            
            logger.info({"message": result})
        except Exception as e:
            logger.error(f"{ct.LLM_RESPONSE_DISP_ERROR_MESSAGE}\n{e}")
            st.error(utils.build_error_message(ct.LLM_RESPONSE_DISP_ERROR_MESSAGE))
            st.stop()

    # # スクロールアンカーの設置：最下部
    # st.subheader(anchor_ids[2], anchor=anchor_ids[2])

    # ==========================================
    # 4. 会話ログへの追加
    # ==========================================
    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": result})

    # 回答生成時に画面を最下部までスクロール
    components.html(
    """
    <div id="scroll_position"></div>
    <script>
        setTimeout(function() {
            var target = document.getElementById("scroll_position");
            if (target) {
                target.scrollIntoView({behavior: "smooth", block: "start"});
            } 
        }, 400);
    </script>
    """,
    height=0,
    )