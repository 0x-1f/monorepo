# 0x1F ft_transcendence frontend repository

## How to run

1. Clone this repository into your local folder
```bash
git clone https://github.com/0x-1f/fe.git
```

2. change directory and install npm packages
```bash
cd fe
npm i
```

3. run dev server
```bash
npm run dev
```

4. connect to the dev server

[https://localhost:5173](https://localhost:5173)

## How to use i18n manager (aka localeManager)

1. import the `t` from localeManager. Absolute path is given below:
```js
import { t } from '/src/modules/locale/localeManager.js';
```

2. the `t` will do everything for us:
```js
t('key', 'fallback paragraph')
```

3. the parameter `key` should be stored in the locale file (stored under `/locale/{locale}.json`). If not, the fallback paragraph will be displayed.

4. sample usage
```javascript
app.innerHTML = `<p style="text-align: left">${t('error', 'sorry')}</p>`
```

5. if the `t` has third parameter(mostly `locale`), just simply delete it. It is just legacy.

## Docker

```bash
docker build -t 0x1f-fe .
docker run 8080:80 0x1f-fe
```