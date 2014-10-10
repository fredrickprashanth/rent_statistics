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
  var nr_done = 0;
  var bds = new Array(1, 2, 3, 4);
  for (var bd = 0; bd < 5; bd++) {
    bds.forEach(function(bd, i, arr) {
      get_city_mean_rent_bd(city, bd, function(err, bd, mean_rent, count) {
        if (err) {
          mean_rent_cb(err, rent_data);  
        } else {
          rent_data.push([mean_rent, count]);
          if (++nr_done == 4) {
            mean_rent_cb(err, rent_data);
          }
        }
      }); // get_city_mean_rent_bd
    }); // forEach
  } // for
} // get_city_mean_rent

exports.get_cities = function(cities_cb) {
  redis_client.lrange("cities", 0, -1, function(err, cities) {
    cities_cb(err, cities);
  });
}
