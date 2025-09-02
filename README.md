現時点の課題
1.2回目以降の質問はスクロールされなくなり読みづらい
2.品切れの商品でもレコメンドされる

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