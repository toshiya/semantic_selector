var wordcheck = require('danger-plugin-wordcheck').default
schedule(wordcheck("./.github/WORDCHECK.txt"))
