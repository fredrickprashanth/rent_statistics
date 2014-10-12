var redis = require("redis");
var redis_client = redis.createClient();

var get_city_mean_rent_bd = function(city, bd, mean_rent_cb) {
  var rent_key = "rent_data:" + city + ":" + bd +":mean";
  redis_client.get(rent_key, function(err, mean_rent) {
    var count_key = "rent_data:" + city + ":" + bd +":count";
    redis_client.get(count_key, function(err, count) {
      mean_rent_cb(err, bd, mean_rent, count);
    });
  });
}

exports.get_city_mean_rent = function(city, mean_rent_cb) {
  var rent_data = new Array();
  var bds = new Array(1, 2, 3, 4);
  bds.forEach(function(bd, i, arr) {
    get_city_mean_rent_bd(city, bd, function(err, bd, mean_rent, count) {
      if (err) {
        mean_rent_cb(err, rent_data);  
      } else {
        rent_data.push({bd:bd, rent:mean_rent, count:count});
        if (rent_data.length == bds.length)
          mean_rent_cb(err, rent_data);
      }
    }); // get_city_mean_rent_bd
  }); // forEach
} // get_city_mean_rent

exports.get_cities = function(cities_cb) {
  redis_client.lrange("cities", 0, -1, function(err, cities) {
    cities_cb(err, cities);
  });
}
