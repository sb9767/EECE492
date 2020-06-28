import sys
import pyzed.sl as sl
from time import sleep


def main():
    cam = sl.Camera()
    init = sl.InitParameters()
    init.depth_mode = sl.DEPTH_MODE.ULTRA
    init.coordinate_units = sl.UNIT.METER
    init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
        print("Reading SVO file: {0}".format(filepath))
        init.set_from_svo_file(filepath)

    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit(1)

    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.STANDARD
    runtime.measure3D_reference_frame = sl.REFERENCE_FRAME.WORLD
    spatial = sl.SpatialMappingParameters()

    transform = sl.Transform()
    tracking = sl.PositionalTrackingParameters(transform)
    cam.enable_positional_tracking(tracking)

    pymesh = sl.Mesh()
    pyplane = sl.Plane()
    reset_tracking_floor_frame = sl.Transform()
    found = 0
    print("Processing...")
    i = 0
    while i < 1000:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS :
            err = cam.find_floor_plane(pyplane, reset_tracking_floor_frame)
            if i > 200 and err == sl.ERROR_CODE.SUCCESS:
                found = 1
                print('Floor found!')
                pymesh = pyplane.extract_mesh()
                break
            i+=1

    if found == 0:
        print('Floor was not found, please try with another SVO.')
        cam.close()
        exit(0)

    cam.disable_positional_tracking()
    save_mesh(pymesh)
    cam.close()
    print("\nFINISH")


def save_mesh(pymesh):
    while True:
        res = input("Do you want to save the mesh? [y/n]: ")
        if res == "y":
            msh = sl.ERROR_CODE.FAILURE
            while msh != sl.ERROR_CODE.SUCCESS:
                filepath = input("Enter filepath name: ")
                msh = pymesh.save(filepath)
                print("Saving mesh: {0}".format(repr(msh)))
                if msh:
                    break
                else:
                    print("Help : you must enter the filepath + filename without extension.")
            break
        elif res == "n":
            print("Mesh will not be saved.")
            break
        else:
            print("Error, please enter [y/n].")

if __name__ == "__main__":
    main()
