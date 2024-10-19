import time 

# STA , BIN.py


time_queue = {
    0 : {
        
        "time" : 0,
        "wait_state" : False
    },
    1 : {
        
        "time" : 0,
        "wait_state" : False
    },
    2 : {
        
        "time" : 0,
        "wait_state" : False
    },
    3 : {
        
        "time" : 0,
        "wait_state" : False
    }
    
}

def turn_on_buzzer():
    print("BUZZER ON")
    
    
def turn_off_buzzer():
    print("BUZZER OFF")

def change_state(index,state):
    
    
    time_queue[index]["time"] = 0 if state=="OFF" else 30
    time_queue[index]["wait_state"] = False if state=="OFF" else True
    

change_state(0,"ON")


remaining_time  = 60


def check_state():
    
    isON = False
    for index in range(4):
        wait_state  = time_queue[index]["wait_state"]
        curr_time = time_queue[index]["time"]
        
        # print()
        
        if wait_state == True:
            if curr_time  == 0:
                isON = True
                # turn_on_buzzer()
            else:
                curr_time -= 1
                
        time_queue[index]["time"] = curr_time
    
    
    print(time_queue)
    return isON


while remaining_time != 0 :
    
    # for i in range()
    
    print(remaining_time)
    
    if check_state():
        turn_on_buzzer()
    else:
        turn_off_buzzer()
        
        
    # if remaining_time == 45:
    #     change_state(0,"OFF")

    
    
    
    remaining_time -= 1
    
    time.sleep(1)

# change_state(0,"OFF")






print(time_queue)
