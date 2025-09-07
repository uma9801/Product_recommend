未解決課題
streamlit（LLMやRAG？）とJavaScript及びスクロールの相性問題

2025/9/7
改善内容：品切れの商品でもレコメンドされる
LLMに在庫のある商品のIDを関連度順に答えさせる。
回答をもとにRetriever結果を並び替えて、1番目の商品についてレコメンドする。
    rank_in_stock_products_by_relevance関数で在庫有無・関連度順ソート・LLM回答の辞書化までを行い、display_product関数のLLM回答を辞書化する部分を削除
    
2025/9/3
ライブラリ：Streamlit-scroll-navigation の導入を試すが失敗（エラーログから抜粋：商品レコメンドに失敗しました。no such table: collections）
    以下をmain.pyに記述するのはエラーなし
    from streamlit_scroll_navigation import scroll_navbar
    # Anchor IDs and icons
    anchor_ids = ["About", "Features", "Settings", "Pricing", "Contact"]
    anchor_icons = ["info-circle", "lightbulb", "gear", "tag", "envelope"]
        続いて以下を記述すると商品レコメンド失敗のエラーが発生が出るようになる。以降の再読み込みでも初期化エラーが出る
        （サイドバーやタイトル直下だと1回目の回答生成からエラー。LLMからの回答後（最下部）に設置だと1回目は正常動作するが2回目からエラーとなる）
        関数 cn.display_product(result) に入れ込むも最下部設置時と同じ動作になる。

        # 2. horizontal menu
        st.subheader("Example 2")
        scroll_navbar(
                anchor_ids,
                key = "navbar2",
                anchor_icons=anchor_icons,
                orientation="horizontal")

            以下、Copilotの見解
            なぜ「horizontal menu」の追加でこのエラーが出るのか？
                1. scroll_navbar自体はデータベースに影響しない
                scroll_navbarやサブヘッダーの追加は、本来データベースには直接関係ありません。
                しかし、ページ構成や初期化処理の順序が変わることで、
                Streamlitの再実行タイミングやセッション状態の初期化タイミングに影響が出る場合があります。

                2. 初期化処理とデータベースの状態
                initialize()内でChroma.from_documents()を呼び出していますが、
                ここで内部的にChroma（ベクトルDB）がcollectionsテーブルを参照しようとします。
                通常はChroma.from_documents()がテーブルを自動生成しますが、
                何らかの理由でテーブルが作成されていない、または破損している場合、このエラーが発生します。
                3. ページ構成の変更による副作用
                Streamlitはコードの構成やウィジェットの追加・順序変更によって、
                セッション状態や初期化処理のタイミングが変わることがあります。
                その結果、初期化処理が正しく走らず、DBのテーブルが未作成のままアクセスしようとしてエラーになることがあります。

2025/9/2
解決:2回目以降の質問はスクロールされなくなり読みづらい
    javascriptを有効化させ、target.scrollIntoViewで最下部にスクロールさせる。
        streamlitの特性で、スクロールのターゲットとなるidを途中で埋め込めず、最後（Scrollintoview実行直前）にしか埋め込めなかった。途中の埋め込みはスクロール前に消える。

2025/9/2
初期化のエラー多発により、最初の課題提出時までロールバック。以下はそれまでの記録であり、9/2以降には適応されない。

初期質問時は最下部までスクロール、2回目以降はスクロールなし。
    下記のダミー要素追加とst.components.v1.html()の追加、さらにsetTimeoutの使用で毎回最下部までスクロールするようになった。
    setTimeoutでJavaScriptの実行タイミングを遅らせないと、Streamlitの再描画タイミングとJavaScriptの実行タイミングがズレてしまい、スクロールが行われない。

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

    チャット入力後などにdiv id="scroll_target"を仕込んでそこにスクロールさせようとしたが、streamlitの描画タイミングの問題で実現不可
    components.pyの関数def display_product(result):に仕込むのも同様
        （Scroll target not foundが出る。つまり、再描画でscroll_targetが消えている。main.pyのcomponents.html()内に直接入れ込めばtargetが残るくらいの再描画サイクル）

        import streamlit.components.v1 as components
        components.html(
            """
            // ここでid="scroll_target"を仕込めば認識する（消えない）

            <div id="target_check_result" style="color: red; font-weight: bold;"></div>
            <script>
                setTimeout(function() {
                    var target = document.getElementById("scroll_target");
                    var resultDiv = document.getElementById("target_check_result");
                    if (target) {
                        resultDiv.innerText = "Scroll target found";
                        target.scrollIntoView({behavior: "smooth", block: "end"});
                    }
                    else {
                        resultDiv.innerText = "Scroll target not found";
                    }
                }, 500);
            </script>
            """,
            height=40,
        )


Copilotより：
Streamlitの描画は「Pythonコードの実行順」ではなく「ウィジェットごとの描画位置」で決まる
    st.markdownやst.chat_messageなどで描画した内容は、Streamlitのレイアウトエンジンによって自動的に配置されます。
    一方、components.html(...)で挿入したHTMLは、その関数が呼ばれた位置に「独立したiframe」として描画されます。


LLMの回答のストリーミング
    st.session_state.llm = ChatOpenAI(model_name=ct.MODEL, temperature=ct.TEMPERATURE, streaming=True)


現状の問題点
    初期化失敗
    LLM回答失敗
        プロンプトに適切に値を渡せていない？
            主題とズレているので一旦保留

    至った経緯：retrieverの検索結果をそのまま回答に使用していたので、検索結果をLLMに渡して在庫のあるものを提示させようとした。
        Retrieverはinitializeでできているので、そこからのrag_chainを作成した
            chat_messageでrag_chainをinvokeしようとして上手く行っていない
                rag_chainは課題2の流用（会話履歴がない点で齟齬があり）