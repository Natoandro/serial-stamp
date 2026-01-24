### Examples

```bash
python3 ticket_number.py \
    -i images/billet-concert.jpeg \
    -o tickets-2.pdf \
    --stack-size 10 -r 2x7 -g 10 -m 10 \
    -t '#N° $no' -t x=600,y=245,size=16 \
    -t '#N° $no' -t x=40,y=245,size=16 \
    -p no,value=561-700
```

```bash
python3 main.py bka.toml -o bka-test.pdf

```
