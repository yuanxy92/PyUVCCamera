from UVCCamera import *

def main():
    cam_num = 2
    fps = 15
    frame_num = 100

    ray.init()
    sync_signal = SyncSignal.remote()
    workers = [cam_worker.remote(i, frame_num) for i in range(cam_num)]
    res = ray.get([workers[i].init_camera.remote() for i in range(cam_num)])
    print(res)
    processes = [workers[i].capture_soft_sync.remote(sync_signal) for i in range(cam_num)]
    
    period_time = 1.0/fps
    sleep_time = period_time / 2
    for i in range(frame_num):
        ray.get(sync_signal.set_signal.remote(0))
        time.sleep(sleep_time)
        ray.get(sync_signal.set_signal.remote(i + 1))
        time.sleep(sleep_time)
    ray.get(sync_signal.set_signal.remote(-1))

    time.sleep(2)
    print(ray.get([workers[i].save_img.remote('./data') for i in range(cam_num)]))

if __name__ == "__main__":
    main()