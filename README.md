# Voucher_Calculation

This program returns the voucher amount based on the segment provided. Please follow the steps for the results.

Step 1 : Use any IDE to run the code. (make sure you have all the required packages)

Step 2 : Open the browser and search for the following url.

   http://127.0.0.1:5000/customerData?customer_id=1&country_code=Peru&last_order_ts=2018-05-03 00:00:00&first_order_ts=2017-05-03 00:00:00&total_orders=15&segment_name=recency_segment

   This URL contains parameters to be given to the program as input.
         {
   "customer_id": 123, // customer id
	 "country_code": "Peru",  // customer’s country
	 "last_order_ts": "2018-05-03 00:00:00",  // ts of the last order done by customer
	 “first_order_ts”: "2017-05-03 00:00:00", // ts of the first order done by customer
	 "total_orders": 15, // total orders done by customer
	 "segment_name": "recency_segment" // which segment customer belongs to
    }
    
Step 3 : See the output on the same browser tab: {'voucher_amount':2640.0}

