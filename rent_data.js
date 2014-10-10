var redis = require("redis");
var redis_client = redis.createClient();

var rent_mean_chart_data = function(city, cb) {
  var rent_data = [];
	var get_mean_rent = function(city, bd, mean_rent_cb) {
		var rent_key = "rent_data:" + city + ":" + bd +":mean";
		redis_client.get(rent_key, function(err, mean_rent) {
			var count_key = "rent_data:" + city + ":" + bd +":count";
			redis_client.get(count_key, function(err, count) {
				mean_rent_cb(bd, mean_rent, count);
			});
		});
	}
	var completed_bd = 0;
	for (bd_i = 1; bd_i < 5; bd_i++) {
		
		get_mean_rent(city, bd_i, function(bd, mean_rent, count) {
      rent_data.push(mean_rent);
			if (++completed_bd == 4) {
				cb(rent_data);
			}
		});
	}
			
}

exports.get_rent_chart_data = function(req, res) {
	rent_mean_chart_data(req.params.city, function(data) {
		res.json(data);
	});	
}

exports.get_rent_chart = function(req, res) {
	redis_client.lrange("cities", 0, -1, function(err, cities) {
		res.render("rent_chart", {"cities": cities});
	});
}


	
	
		

		
	

