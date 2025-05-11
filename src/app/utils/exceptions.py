from fastapi import HTTPException

EXC_401_INVALID_USERNAME_OR_PASSWORD = HTTPException(status_code=401, detail='Invalid username or password')
EXC_404_BOOK_NOT_FOUND = HTTPException(status_code=404, detail="Book not found")
EXC_404_USER_NOT_FOUND = HTTPException(status_code=404, detail='User not found')
EXC_400_USERNAME_TAKEN = HTTPException(status_code=400, detail='This username is already taken')
EXC_403_NOT_ENOUGH_MONEY = HTTPException(status_code=403, detail='Not enough money')
EXC_400_BOOK_ALREADY_BOUGHT = HTTPException(status_code=400, detail='You already bought this book')
EXC_400_BOOK_NOT_BOUGHT = HTTPException(status_code=400, detail='You have not purchased this book')
EXC_403_INVALID_TOKEN = HTTPException(status_code=403, detail='Invalid token: you do not have access to this function')