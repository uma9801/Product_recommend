"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import streamlit as st
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown("こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。")
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """
    商品情報の表示

    Args:
        result: LLMからの回答（Documentオブジェクト）
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # resultのテキストを辞書に変換（Documentオブジェクトのpage_contentの中身は単なる文字列(str型)なので、辞書に変換する必要がある）
    # result[0]で1件のみを表示
    product_lines = result[0].page_content.split("\n")
    logger.info({"辞書化のために\nで分割": product_lines})

    product = {item.split(": ")[0]: item.split(": ")[1] for item in product_lines}
    logger.info({"辞書に変換": product})
    # 商品情報の表示
    st.markdown("以下の商品をご提案いたします。")

    # 「商品名」と「価格」
    st.success(f"""
            商品名：{product['name']}（商品ID: {product['id']}）\n
            価格：{product['price']}
    """)

    # 在庫数の表示
    if product["stock_status"] == "なし":
        st.error(ct.OUT_OF_STOCK_MESSAGE, icon=ct.ERROR_ICON)
    elif product["stock_status"] == "残りわずか":
        st.warning(ct.LOW_STOCK_WARNING_MESSAGE, icon=ct.WARNING_ICON)

    # 「商品カテゴリ」と「メーカー」と「ユーザー評価」
    st.code(f"""
        商品カテゴリ：{product['category']}\n
        メーカー：{product['maker']}\n
        評価：{product['score']}({product['review_number']}件)
    """, language=None, wrap_lines=True)

    # 商品画像
    st.image(f"images/products/{product['file_name']}", width=400)

    # 商品説明
    st.code(product['description'], language=None, wrap_lines=True)

    # おすすめ対象ユーザー
    st.markdown("**こんな方におすすめ！**")
    st.info(product["recommended_people"])

    # 商品ページのリンク
    st.link_button("商品ページを開く", type="primary", use_container_width=True, url="https://google.com")

def rank_in_stock_products_by_relevance(result, user_input):
    """
    在庫ありの商品を抽出し、ユーザー入力との関連度順にresult内を並び替える

    Args:
        result: Retrieverの結果（Documentオブジェクトリスト）
        user_input: ユーザーの入力内容（str）
    """
    # 各商品情報は右記の情報でくくられている：'id': '', 'name': '', 'category': '', 'price': '', 'maker': '', 'recommended_people': '', 'review_number': '', 'score': '', 'file_name': '', 'description': '', 'stock_status': ''
    # 'stock_status': ''が'なし'の商品を除外するプロンプトをLLMに与え、在庫あり商品のみを抽出するように指示する。
    # Retriverの結果として引数のresultを受け取り、それをcontextとしてLLMに与える。

    logger = logging.getLogger(ct.LOGGER_NAME)

    llm = st.session_state.llm
    context = "\n\n".join([r.page_content for r in result])
    prompt = ct.RANK_IN_STOCK_PRODUCTS_PROMPT.format(context=context, user_input=user_input)

    # LLMにプロンプトを投げる
    response = llm(prompt) # 例: "5,13,22"
    logger.info({"在庫あり商品を関連度順に並び替えたLLMの回答": response})

    # response内のcontentに格納されているIDリストを抽出
    in_stock_ids = [id_.strip() for id_ in response.content.split(",")]
    logger.info({"LLMの回答からIDリストのみを抽出": in_stock_ids})

    # Documentオブジェクトの形を保ったまま、resultの中身をin_stock_idsのID順に並び替える
    result_sorted = []
    for id_ in in_stock_ids:
        for r in result:
            product_lines = r.page_content.split("\n")
            product_dict = {item.split(": ")[0]: item.split(": ")[1] for item in product_lines if ": " in item}
            product_id = product_dict.get("id")
            if product_id == id_:
                result_sorted.append(r)
                break
    logger.info({"IDリストをもとにRetrieverの結果を編集": result_sorted})
    return result_sorted