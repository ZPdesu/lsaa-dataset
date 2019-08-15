var panorama = require('google-panorama-by-id');
var jsonfile = require('jsonfile');
var id = process.argv[2]; //'DsK88fpAYl9NpNsM2yKMMA'
var file_location = process.argv[3];

//console.log("Called with:", id);


panorama(id, function (err, result) {
  if (err) throw err;
  //var json = JSON.stringify(result)
  jsonfile.writeFile(file_location, result);
  //console.log(result)
})




