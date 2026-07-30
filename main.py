try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.fetch_defillama import get_new_candidates
from scripts.groq_analyze import analyze_airdrop
from scripts.notify import send_message

def main():
    print("Airdrop Radar baslatiliyor...")

    candidates = get_new_candidates()

    if not candidates:
        send_message("Airdrop Radar - Bugun yeni aday bulunamadi.")
        print("Yeni aday yok, islem durduruldu.")
        return

    print(str(len(candidates)) + " yeni aday bulundu, analiz ediliyor...")

    analyzed = []
    for i, c in enumerate(candidates):
        print(str(i+1) + "/" + str(len(candidates)) + " analiz ediliyor: " + c["name"])
        steps = analyze_airdrop(c)
        c["steps"] = steps
        analyzed.append(c)
        time.sleep(2)

    top5 = analyzed[:5]
    lines = ["Airdrop Radar - " + str(len(analyzed)) + " Yeni Aday Bulundu!", ""]
    lines.append("En Yuksek TVL - Ilk 5:")
    lines.append("")

    for i, c in enumerate(top5, 1):
        tvl_m = c["tvl"] / 1_000_000
        lines.append(str(i) + ". " + c["name"] + " - $" + str(round(tvl_m, 1)) + "M | " + c["chain"])
        lines.append(c["steps"])
        lines.append("")

    send_message("\n".join(lines))
    print("Tamamlandi.")

if __name__ == "__main__":
    main()
