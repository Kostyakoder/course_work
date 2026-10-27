import subprocess
import sys


buffer = sys.stdin.buffer.read()
process = subprocess.Popen(['pandoc', '-f', 'docx', '-t', 'html'],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
process.stdin.write(buffer)
process.stdin.close()
print(process.stdout.read().decode('utf-8'), end='')