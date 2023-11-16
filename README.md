### What:
Docker solution for [imgproxy](https://github.com/imgproxy/imgproxy).

Target OS: Ubuntu

---
### How:
0. Install Docker and Compose if you need:
```sh
docker_install.sh
```

1. Run:
```sh
python setup.py
python set_workers_num.py
```
2. Check and set vars in the `.env` file.

3. Run:
```sh
docker compose up -d
```

---
