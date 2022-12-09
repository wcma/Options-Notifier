def compiler(event, context):
    print("test")
    return {
        "statusCode": 200
    }
if __name__ == '__main__':
    print(compiler(None, None))
    
