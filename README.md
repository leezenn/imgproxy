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
### Proxy rota:
- clone repo:
```sh
git clone https://github.com/leezenn/imgforkxy.git
```

- build the image:
```sh
cd imgforkxy
./docker_build.sh
```

- specify creds at `.env`.
>[!NOTE]
>Proxied via HTTP, port `:80`
>It will use regular downloader if any of the cred is missing.  
> If you have no need in proxy: Official image is commented out in `docker-compose.yml`

---