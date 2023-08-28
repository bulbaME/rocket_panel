def check_response(res):
    if res['status'] == 'error':
        raise Exception('An error occured: ' + res['message'])
    
    return res