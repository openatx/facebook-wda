# How to run tests
the test is based on py.test, and you need to install python3

```bash
export DEVICE_URL="http://localhost:8100"
cd tests
py.test -vv
```

# 已知问题
- iOS 13.5
  顶部有通知栏时，alert操作不了

# HTTP Request
```
$ http GET $DEVICE_URL/HEALTH
I-AM-ALIVE

$ curl -X POST -d '{"name": "home"}' 'http://localhost:8100/session/024A4577-2105-4E0C-9623-D683CDF9707E/wda/pressButton'
Return (47ms): {
  "status" : 0,
  "sessionId" : "024A4577-2105-4E0C-9623-D683CDF9707E",
  "value" : null
}

$ curl -X POST -d '{"value": ["h", "e", "l", "l", "o"]}' 'http://localhost:8100/session/024A4577-2105-4E0C-9623-D683CDF9707E/wda/keys'
{
  "status" : 0,
  "sessionId" : "024A4577-2105-4E0C-9623-D683CDF9707E",
  "value" : null
}
```