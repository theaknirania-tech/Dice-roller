Last login: Tue May 19 10:27:26 on ttys001
govinddhingra@Govinds-Laptop untitled folder % >....                            
            tk.Label(
                row, text=dice_str,
                font=("Courier New", 12),
                bg=row["bg"], fg=HIGHLIGHT if i == 0 else "white",
            ).pack(side="left")

            tk.Label(
                row, text=f"= {record['total']}",
                font=("Courier New", 10, "bold"),
                bg=row["bg"], fg=HIGHLIGHT if i == 0 else MUTED_COLOR,
            ).pack(side="right")


# ─── Entry Point ─────────────────────────────────────────────
def main():
    root = tk.Tk()
    app  = DiceRollerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

