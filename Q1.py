import re
import os


def def_word_cnt(string: str) -> dict:
    word_cnt = {}
    string = re.sub(r"[^\w\s]", "", string)

    for word in string.strip().lower().split():
        if word in word_cnt.keys():
            word_cnt[word] += 1
        else:
            word_cnt[word] = 1

    return word_cnt


def main():
    string = "Ban la thi sinh tuyet voi nhat ma toi tung gap. Ban qua xuat sac, qua tuyet voi!"
    word_cnt = def_word_cnt(string)

    # Save to result.xml
    print("Writing to result.xml")
    with open("result.xml", "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<word_cnt>\n")
        for word, cnt in word_cnt.items():
            f.write(f"\t<word>\n\t\t<value>{word}</value>\n\t\t<count>{cnt}</count>\n\t</word>\n")
        f.write("</word_cnt>\n")

    # Generate a list of filenames
    file_names = [f"results/result_{i}.xml" for i in range(1, 101)]
    # Create folder name "results", if not exist
    of.mkdir("results") if not os.path.exists("results") else None
    # Create the result string
    result_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<word_cnt>\n"
    for word, cnt in word_cnt.items():
        result_string += f"\t<word>\n\t\t<value>{word}</value>\n\t\t<count>{cnt}</count>\n\t</word>\n"
    result_string += "</word_cnt>\n"
    # Write to local disk
    print("Writing to local disk")
    list(map(lambda x: open(x, "w").write(result_string), file_names))


if __name__ == "__main__":
    main()