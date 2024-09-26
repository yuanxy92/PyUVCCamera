from UVCCamera import *
import winsound

def main():
    cam_num = 6
    fps = 10
    frame_num = 900
    out_dir = './data/data_0829_10'
    os.makedirs(out_dir, exist_ok=True)
    
    # init parallel camera using ray  
    cam_indices = [0, 1, 2, 4, 5, 6]
    ray.init()
    sync_signal = SyncSignal.remote()
    workers = [UVCCamera.remote(cam_indices[i], frame_num) for i in range(cam_num)]
    res = ray.get([workers[i].init_camera.remote() for i in range(cam_num)])
    print(res)
    processes = [workers[i].capture_soft_sync.remote(sync_signal) for i in range(cam_num)]
    
    # generate ray signals to capture images
    print('Images capturing start in 3 seconds')
    winsound.Beep(600, 500)
    time.sleep(1)
    print('Images capturing start in 2 seconds')
    winsound.Beep(600, 500)
    time.sleep(1)
    print('Images capturing start in 1 seconds ')
    winsound.Beep(600, 500)
    time.sleep(1)
    print('Capturing ... ')
    
    period_time = 1.0/fps
    sleep_time = period_time / 2
    for i in range(frame_num):
        ray.get(sync_signal.set_signal.remote(0))
        time.sleep(sleep_time)
        ray.get(sync_signal.set_signal.remote(i + 1))
        time.sleep(sleep_time)
    ray.get(sync_signal.set_signal.remote(-1))

    # generate ray signals to save images
    time.sleep(0.5)
    print(ray.get([workers[i].save_img.remote(out_dir) for i in range(cam_num)]))

    print('Images saved!')
    winsound.Beep(600, 2000)

if __name__ == "__main__":
    main()