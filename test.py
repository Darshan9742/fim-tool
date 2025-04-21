import hashlib

def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

print(hash_file("D:\ENGINEERING NOTES\8th sem\Internship\qtest\qwerty.txt"))
