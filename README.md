Ondilo ICO
==========

[![PyPi](https://img.shields.io/pypi/v/ondilo.svg)](https://pypi.python.org/pypi/ondilo)
[![PyPi](https://img.shields.io/pypi/l/ondilo.svg)](https://github.com/JeromeHXP/ondilo/blob/master/LICENSE.txt)

A simple client used to access Ondilo ICO APIs.  
Implemented to be used in Home Assistant, but can be used anywhere else.

Install
-------

To install ondilo, run:

    pip install ondilo

Example usage
-------------

Ondilo is using the Authorization Code Grant flow, so each user must be individually authenticated.  
The ```client_id``` and ```client_secret``` are always the same, there is no need to create a specific app on Ondilo side. So they are hard coded. However, if needed, they can also be passed during initialization.   

A very basic implementation could look like:

    from ondilo import Ondilo

    client = Ondilo(redirect_uri="https://example.com/api")
    print('Please go here and authorize,', client.get_authurl())

    redirect_response = input('Paste the full redirect URL here:')
    client.request_token(authorization_response=redirect_response)

    print("Found all those pools: ", client.get_pools())


If the Oauth2 flow is handled externally and a token is already available, one can also use the package this way:  

    from ondilo import Ondilo

    client = Ondilo(token)
    print("Found all those pools: ", client.get_pools())

Available APIs
--------------

More information about the returned objects can be found here: https://interop.ondilo.com/docs/api/customer/v1/


- ```get_pools```: Get list of available pools / spa
- ```get_ICO_details```: Get details of a pool/spa
- ```get_last_pool_measures```: Get the last measures from an ICO
- ```get_pool_recommendations```: Get the list of recommendations from an ICO
- ```validate_pool_recommendation```: Acknowledge a recommendation
- ```get_user_units```: Get user units
- ```get_user_info```: Get user infos
- ```get_pool_config```: Get pool/spa ranges for temperature, pH, ORP, salt and TDS
- ```get_pool_shares```: Get list of users with whom the pool/spa is shared
- ```get_pool_histo```: Get measurements historical data

