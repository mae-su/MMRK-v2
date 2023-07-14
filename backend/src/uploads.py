import uploadserver
uploadserver.CSS={
    'light': '',
    'auto': '''<style type="text/css">
@media (prefers-color-scheme: dark) {
  body {
    font-family: 'Roboto', sans-serif;
    background-color: #000;
    color: #fff;
  }
}
</style>''',
    'dark': '''<style type="text/css">
body {
  background-color: #000;
  color: #fff;
  font-family: 'Roboto', sans-serif;
}
h1 {
  font-weight: 100
}
</style>'''
}
uploadserver.serve_forever()