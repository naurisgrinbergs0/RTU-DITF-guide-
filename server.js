// import required modules
const express = require('express');
const path = require('path');
const routes = require('./routes');
const fs = require('fs');

const app = express();

// define a route handler for the root URL
app.use(express.static(path.join(__dirname)));
app.use(routes);

// empty the picture directory, so that they don't pile up
const pic_directory = './path_finder/path_pics';
fs.readdir(pic_directory, (err, files) => {
  if (err) throw err;

  for (const file of files) {
    fs.unlink(path.join(pic_directory, file), err => {
      if (err) throw err;
    });
  }
});

// start the server
const port = 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
