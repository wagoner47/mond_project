import mond_project
import h5py
import pandas as pd
import numpy as np
import os

def main():
    h = 0.704
    query_params = {"stars":"Coordinates,Masses,Velocities",
            "gas"  :"Coordinates,Masses,Velocities"}
    snap_url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/"
    snap = mond_project.get(snap_url)
    a = 1.0 / (1.0 + snap["redshift"])
    file_base_z = "Illustris-1_z=0_subhalo{}.pickle.gz"
    file_base_sn = "Illustris-1_snapnum=135_subhalo{}.pickle.gz"
    target_dir = os.path.join(os.getcwd(), "test_data", "exp")
    if os.path.isfile(target_dir):
        os.rename(target_dir, target_dir + ".file")
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    id_list = []
    subi = mond_project.get(snap["subhalos"])
    for halo in subi["results"]:
        haloi = mond_project.get(halo["url"])
        if haloi["mass_stars"] > 0.0 and haloi["mass_gas"] > 0.0:
            id_list.append(haloi["id"])
    if not (os.path.isfile(os.path.join(target_dir,
        file_base_z.format(id_list[0]))) or
        os.path.isfile(os.path.join(target_dir,
            file_base_sn.format(id_list[0])))):
        halo0 = mond_project.get(snap_url + "subhalos/" + str(id_list[0]))
        halo_pos = np.array([halo0["pos_x"], halo0["pos_y"], halo0["pos_z"]])
        halo_vel = np.array([halo0["vel_x"], halo0["vel_y"], halo0["vel_z"]])
        file0 = mond_project.get(halo0["cutouts"]["subhalo"], query_params)
        with h5py.File(file0, "r") as f:
            r_gas = np.array([np.sqrt(np.sum([deltai**2 for deltai in (posi - 
                halo_pos)])) for posi in f["PartType0"]["Coordinates"]],
                dtype=float) * a / h
            m_gas = np.asarray(f["PartType0"]["Masses"], dtype=float) * 10**10 / h
            v_gas = np.array([np.sqrt(np.sum([deltai**2 for deltai in (veli -
                halo_vel)])) for veli in f["PartType0"]["Velocities"] *
                np.sqrt(a)], dtype=float)
            t_gas = np.full(r_gas.size, "gas")
            r_stars = np.array([np.sqrt(np.sum([deltai**2 for deltai in (posi -
                halo_pos)])) for posi in f["PartType4"]["Coordinates"]],
                dtype=float) * a / h
            m_stars = np.asarray(f["PartType4"]["Masses"], dtype=float) * 10**10 / h
            v_stars = np.array([np.sqrt(np.sum([deltai**2 for deltai in (veli -
                halo_vel)])) for veli in f["PartType4"]["Velocities"] *
                np.sqrt(a)], dtype=float)
            t_stars = np.full(r_stars.size, "star")
            df = pd.DataFrame.from_dict({"r": np.append(r_gas, r_stars), "M":
                np.append(m_gas, m_stars), "v": np.append(v_gas, v_stars), "type":
                np.append(t_gas, t_stars)})
            df.to_pickle(os.path.join(target_dir,
                file_base_z.format(id_list[0])))
            df.to_pickle(os.path.join(target_dir,
                file_base_sn.format(id_list[0])))
        os.remove(file0)
    else:
        if not os.path.isfile(os.path.join(target_dir,
            file_base_z.format(id_list[0]))):
            df = pd.read_pickle(os.path.join(target_dir,
                file_base_sn.format(id_list[0])))
            df.to_pickle(os.path.join(target_dir,
                file_base_z.format(id_list[0])))
        elif not os.path.isfile(os.path.join(target_dir,
            file_base_sn.format(id_list[0]))):
            df = pd.read_pickle(os.path.join(target_dir,
                file_base_z.format(id_list[0])))
            df.to_pickle(os.path.join(target_dir,
                file_base_sn.format(id_list[0])))
        else:
            pass
    while subi["next"] is not None and len(id_list) < 100:
        subi = mond_project.get(subi["next"])
        for halo in subi["results"]:
            haloi = mond_project.get(halo["url"])
            if haloi["mass_stars"] > 0.0 and haloi["mass_gas"] > 0.0:
                id_list.append(haloi["id"])
    file_list = [file_base_z.format(halo_id) for halo_id in id_list[:100]]
    np.savez_compressed(os.path.join(target_dir, "subhalo_list_z.npz"),
            file_list)
    file_list = [file_base_sn.format(halo_id) for halo_id in id_list[:100]]
    np.savez_compressed(os.path.join(target_dir, "subhalo_list_snapnum.npz"),
            file_list)

if __name__ == "__main__":
    main()
