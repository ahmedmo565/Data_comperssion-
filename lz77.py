import json

INPUT_FILE = "file1.txt"
COMPRESSED_FILE = "file2.txt"
OUTPUT_FILE = "file3.txt"
SEARCH_SIZE = 4095
LOOK_SIZE = 255


def compress(text):
    tags = []
    i = 0
    while i < len(text):
        best_pos = 0
        best_len = 0
        start = max(0, i - SEARCH_SIZE)
        max_len = min(len(text) - i, LOOK_SIZE)

        for j in range(start, i):
            length = 0
            while length < max_len and text[j + length] == text[i + length]:
                length += 1
            if length > 0 and length >= best_len:
                best_len = length
                best_pos = i - j

        if i + best_len < len(text):
            nxt = text[i + best_len]
        else:
            nxt = None

        tags.append((best_pos, best_len, nxt))
        i += best_len + 1
    return tags


def decompress(tags):
    result = []
    for pos, length, nxt in tags:
        start = len(result) - pos
        for k in range(length):
            result.append(result[start + k])
        if nxt is not None:
            result.append(nxt)
    return "".join(result)


def tag_to_line(tag):
    pos, length, nxt = tag
    if nxt is None:
        sym = "NULL"
    else:
        sym = json.dumps(nxt, ensure_ascii=False)
    return "<%d,%d,%s>" % (pos, length, sym)


def line_to_tag(line):
    line = line.strip()
    pos, length, sym = line[1:-1].split(",", 2)
    if sym == "NULL":
        nxt = None
    else:
        nxt = json.loads(sym)
    return (int(pos), int(length), nxt)


def read_text(name):
    with open(name, "r", encoding="utf-8", newline="") as f:
        return f.read()


def run_compression():
    try:
        text = read_text(INPUT_FILE)
    except FileNotFoundError:
        print("Can't find", INPUT_FILE)
        return

    tags = compress(text)

    with open(COMPRESSED_FILE, "w", encoding="utf-8") as f:
        for tag in tags:
            f.write(tag_to_line(tag) + "\n")

    print("Read", len(text), "characters from", INPUT_FILE)
    print("Wrote", len(tags), "tags to", COMPRESSED_FILE)

    if tags:
        original = len(text) * 8
        pos_bits = max(1, max(t[0] for t in tags).bit_length())
        len_bits = max(1, max(t[1] for t in tags).bit_length())
        tag_bits = pos_bits + len_bits + 8
        compressed = len(tags) * tag_bits
        print("Original size   =", original, "bits")
        print("Tag size        =", pos_bits, "+", len_bits, "+ 8 =", tag_bits, "bits")
        print("Compressed size =", compressed, "bits")
        print("Ratio           = %.3f" % (compressed / original))


def run_decompression():
    try:
        with open(COMPRESSED_FILE, "r", encoding="utf-8") as f:
            lines = [l for l in f.read().split("\n") if l.strip()]
    except FileNotFoundError:
        print("Can't find", COMPRESSED_FILE, "- compress something first")
        return

    tags = [line_to_tag(l) for l in lines]
    text = decompress(tags)

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    print("Read", len(tags), "tags from", COMPRESSED_FILE)
    print("Wrote", len(text), "characters to", OUTPUT_FILE)

    try:
        same = read_text(INPUT_FILE) == text
        print("Same as", INPUT_FILE, "?", same)
    except FileNotFoundError:
        pass


def main():
    while True:
        print()
        print("===== LZ77 =====")
        print("1) Compress   (" + INPUT_FILE + " -> " + COMPRESSED_FILE + ")")
        print("2) Decompress (" + COMPRESSED_FILE + " -> " + OUTPUT_FILE + ")")
        print("3) Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            run_compression()
        elif choice == "2":
            run_decompression()
        elif choice == "3":
            break
        else:
            print("Wrong choice, try again")


if __name__ == "__main__":
    main()
