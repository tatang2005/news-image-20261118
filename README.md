# The World in One Day — Wednesday 18 November 2026

Entry for the make.fun competition **news-image-20261118**: one image that
sums up the world's news of Wednesday 18 November 2026.

The image is a newspaper front page: a dated masthead, six story panels
(Shenzhen summit, Gulf escalation, the Kerch Bridge strike, COP31's decisive
week, Nvidia after Huang, and Cyclone Akvan), and a footer strip with three
more of the day's stories.

## How it works

- `draw.py` draws the front page with PIL (flat geometric icons, big serif
  headlines) and saves it as `entry.png` (1024x1024).
- `main.py` is the entry program: it copies `entry.png` to the output
  directory (`$MAKEFUN_OUTPUT_DIR`, or `/output`).

## Run

```sh
python3 main.py
```

## License

MIT — see `LICENSE`.
