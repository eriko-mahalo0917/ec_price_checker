############################################################
import tkinter as tk
from tkinter import messagebox
############################################################

class PopupManager:

    # -----------------------
    # 1つ目のフロー
    # キーワード入力ダイアログを表示する
    # OKを押したら入力文字列を返す
    # キャンセル・×ボタンは ValueError を送出する
    # -----------------------
    @staticmethod
    def ask_keywords() -> str:
        root = tk.Tk()
        root.withdraw()  # メインウィンドウは非表示

        dialog = tk.Toplevel(root)
        dialog.title("楽天価格チェッカー")
        dialog.resizable(False, False)
        dialog.grab_set()  # ダイアログが閉じるまで操作をブロック

        # ウィンドウを画面中央に配置
        dialog.update_idletasks()
        w, h = 380, 170
        x = (dialog.winfo_screenwidth()  - w) // 2
        y = (dialog.winfo_screenheight() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        # ラベル
        tk.Label(
            dialog,
            text="検索キーワードを入力してください。\nAND検索はカンマ区切りで入力できます。\n例）キーワード1,キーワード2",
            justify="left",
            padx=16,
            pady=10,
        ).pack(anchor="w")

        # 入力欄
        entry_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=entry_var, width=42)
        entry.pack(padx=16, pady=(0, 12))
        entry.focus_set()

        # 結果を保持する変数
        result: dict = {"value": None, "cancelled": True}

        def on_ok(event=None):
            value = entry_var.get().strip()
            if not value:
                messagebox.showwarning("入力エラー", "キーワードを入力してください。", parent=dialog)
                return
            result["value"] = value
            result["cancelled"] = False
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Enterキーでも確定できる
        entry.bind("<Return>", on_ok)
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        # ボタン行
        btn_frame = tk.Frame(dialog)
        btn_frame.pack()
        tk.Button(btn_frame, text="キャンセル", width=10, command=on_cancel).pack(side="left", padx=8)
        tk.Button(btn_frame, text="OK",         width=10, command=on_ok,     default="active").pack(side="left", padx=8)

        root.wait_window(dialog)
        root.destroy()

        if result["cancelled"]:
            raise ValueError("キーワード入力がキャンセルされました。")

        return result["value"]

    # -----------------------
    # 2つ目のフロー
    # 処理完了のポップアップを表示する
    # -----------------------
    @staticmethod
    def show_complete(filepath: str) -> None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "完了",
            f"CSVの保存が完了しました。\n\n{filepath}",
        )
        root.destroy()

    # -----------------------
    # エラーをポップアップで表示する
    # -----------------------
    @staticmethod
    def show_error(message: str) -> None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("エラー", message)
        root.destroy()
