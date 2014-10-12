redis_rent_data = require("./rent_data_redis");

exports.get_rent_chart_data = function(req, res) {
  redis_rent_data.get_city_mean_rent(req.params.city, function(err, data) {
    var rent_data = [];
    data.forEach(function(rent_rec, i, arr) {
      var count = +rent_rec.count;
      if (count)
        rent_data.push(rent_rec);
    });
    res.json(rent_data);
  }); 
}

exports.get_rent_chart = function(req, res) {
  redis_rent_data.get_cities(function(err, cities) {
    res.render("rent_chart", {"cities": cities});
  });
}
