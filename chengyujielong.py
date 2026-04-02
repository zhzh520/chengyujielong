import random

# 加载成语库
def load_idioms(filepath=r"D:\Users\huihu\Desktop\2026\damoxing\RAG\链代码\chengyuku.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return set(lines), lines
    except:
        print("未找到 chengyuku.txt，请把文件放在同一目录")
        return set(), []

idiom_set, idiom_list = load_idioms()

# 构建接龙字典：key=首字，value=成语列表
idiom_map = {}
for idiom in idiom_list:
    if len(idiom) >= 1:
        c = idiom[0]
        if c not in idiom_map:
            idiom_map[c] = []
        idiom_map[c].append(idiom)

# 获取下一个合法成语
def ai_get_idiom(last_char):
    candidates = idiom_map.get(last_char, [])
    if not candidates:
        return None
    return random.choice(candidates)

# 游戏主逻辑
def play_game():
    print("=== 成语接龙对战 ===")
    print("规则：")
    print("1. 必须接尾字")
    print("2. 成语必须在 chengyuku.txt 里，否则直接输")
    print("3. 接不上也算输\n")

    # 玩家先出
    while True:
        user_first = input("请你先出一个成语：").strip()
        if user_first not in idiom_set:
            print("❌ 该成语不在成语库中，你输了！")
            return
        if len(user_first) < 2:
            print("请输入有效成语")
            continue
        break

    current_idiom = user_first
    print(f"你：{current_idiom}")

    while True:
        # AI 回合
        last_char = current_idiom[-1]
        ai_idiom = ai_get_idiom(last_char)

        if not ai_idiom:
            print("🤖 AI 接不上，你赢了！")
            return

        print(f"AI：{ai_idiom}")
        current_idiom = ai_idiom

        # 玩家回合
        while True:
            user_in = input("你：").strip()
            # 检查是否在库中
            if user_in not in idiom_set:
                print("❌ 成语不在库中，你输了！")
                return
            # 检查字数
            if len(user_in) < 2:
                print("请输入有效成语")
                continue
            # 检查接龙字
            if user_in[0] != current_idiom[-1]:
                print(f"❌ 必须以【{current_idiom[-1]}】开头，重新输入！")
                continue
            # 合法
            break

        current_idiom = user_in

if __name__ == "__main__":
    play_game()