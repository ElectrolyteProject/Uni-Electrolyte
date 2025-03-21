import makeit.global_config as gc
from makeit.retrosynthetic.tree_builder import TreeBuilder
from makeit.synthetic.context.neuralnetwork import  NeuralNetContextRecommender
from argparse import ArgumentParser
import os
import pandas as pd
import json
import time
from collections import deque
import rdkit
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
from PIL import Image, ImageDraw, ImageFont

parser = ArgumentParser()
parser.add_argument('--input_csv_file', type=str)
parser.add_argument('--output_dir', type=str)
parser.add_argument("--ID_tag", type=str)
args = parser.parse_args()

input_df = pd.read_csv(args.input_csv_file)
ID_tag=args.ID_tag
output_dir = args.output_dir
# if os.path.exists(output_dir):
#     os.system("rm -rf %s" % (output_dir))
os.system("mkdir %s" % (output_dir))


celery = False
st = time.time()
treeBuilder = TreeBuilder(celery=celery, mincount=25, mincount_chiral=10)
print("treeBuilder spend", time.time() - st)

cont = NeuralNetContextRecommender()
cont.load_nn_model(model_path=gc.NEURALNET_CONTEXT_REC['model_path'], info_path=gc.NEURALNET_CONTEXT_REC['info_path'], weights_path=gc.NEURALNET_CONTEXT_REC['weights_path'])


result_dict = {}
os.system("mkdir %s/tmp"%(output_dir))
for k, v in input_df.iterrows():
    try:
        smiles = v["smiles"]
    except:
        smiles=v["SMILES"]
    ID = v[ID_tag]
    result_dict[ID] = {"smiles": smiles}
    status, paths = treeBuilder.get_buyable_paths(smiles, max_depth=4, template_prioritization=gc.relevance,
                                                  precursor_prioritization=gc.relevanceheuristic, nproc=2,
                                                  expansion_time=60, max_trees=5, max_ppg=10,
                                                  max_branching=25, apply_fast_filter=True, filter_threshold=0.75,
                                                  min_chemical_history_dict={'as_reactant': 5, 'as_product': 1,
                                                                             'logic': 'none'})
    result_dict[ID]["paths"] = paths
    result_dict[ID]["status"] = status
    # if len(paths) < 3:
    #     result_dict[ID]["paths"] = paths
    # else:
    #     result_dict[ID]["paths"] = paths[:3]

output_json_fp=open("%s/output.json"%(output_dir),"w")
json.dump(result_dict, output_json_fp)

# import os
# import pandas as pd
# import json
# import time
# from collections import deque
# import rdkit
# from rdkit.Chem import AllChem
# from rdkit.Chem import Draw
# from PIL import Image

# tmp_dir="./tmp_dir"
# #tmp_dir="./data/rxn_draw"
# if os.path.exists(tmp_dir):
#     os.system("rm -rf %s"%(tmp_dir))
# os.system("mkdir %s"%(tmp_dir))
# result_dict=json.load(open("./output_json_file.json"))


def output_condiction_picture(rxn_smiles):
    width = 1200
    height_each_img = 300
    width_mol = 300
    pil_img_list = []
    font_file="DejaVuSans.ttf" # "arial.ttf" for win

    # 反应的picture
    rxn = AllChem.ReactionFromSmarts(rxn_smiles, useSmiles=True)
    img = Draw.ReactionToImage(rxn, subImgSize=(width_mol, height_each_img))
    pil_img_list.append(img)

    #拼接条件title
    condition_part_img_list = []
    for sth in ("temperature","solvent", "reagents", "catalyst"):
        sth_img = Image.new(pil_img_list[0].mode, (width_mol, height_each_img))  #
        draw = ImageDraw.Draw(sth_img)
        draw.rectangle([(0, 0), sth_img.size], fill=(255, 255, 255))
        text = sth
        position = (50,250)  # 文字的起始位置 (x, y)
        font = ImageFont.truetype(font_file, 24)  # 使用指定字体和大小
        color = (0, 0, 0)  # 文字颜色，RGB 格式
        draw.text(position, text, font=font, fill=color)
        condition_part_img_list.append(sth_img)
    # 创建一个空白画布，用于拼接condition图片
    condition_img = Image.new(pil_img_list[0].mode, (width, height_each_img))  #
    # 在画布上拼接图片
    for img_idx, img in enumerate(condition_part_img_list):
        condition_img.paste(img, (width_mol * img_idx, 0))
    pil_img_list.append(condition_img)

    # 拼接条件picture
    condition_result = cont.get_n_conditions(rxn_smiles_list[0], 10, with_smiles=False)
    # condition_result=json.loads("""
    # [[102.30387878417969, "C1COCCO1", "CCN(CC)CC", "Reaxys Name (1,1'-bis(diphenylphosphino)ferrocene)palladium(II) dichloride", NaN, NaN], [104.92787170410156, "C1COCCO1", "CCN(CC)CC", "Cl[Pd](Cl)([P](c1ccccc1)(c1ccccc1)c1ccccc1)[P](c1ccccc1)(c1ccccc1)c1ccccc1", NaN, NaN], [99.1409912109375, "Cc1ccccc1", "CCN(CC)CC", "Cl[Pd](Cl)([P](c1ccccc1)(c1ccccc1)c1ccccc1)[P](c1ccccc1)(c1ccccc1)c1ccccc1", NaN, NaN], [76.38555908203125, "C1CCOC1", "CCN(CC)CC", "Cl[Pd](Cl)([P](c1ccccc1)(c1ccccc1)c1ccccc1)[P](c1ccccc1)(c1ccccc1)c1ccccc1", NaN, NaN], [95.92562103271484, "Cc1ccccc1", "CCN(CC)CC", "Reaxys Name (1,1'-bis(diphenylphosphino)ferrocene)palladium(II) dichloride", NaN, NaN], [75.68882751464844, "C1CCOC1", "CCN(CC)CC", "Reaxys Name (1,1'-bis(diphenylphosphino)ferrocene)palladium(II) dichloride", NaN, NaN], [93.39191436767578, "C1COCCO1", "", "Reaxys Name (1,1'-bis(diphenylphosphino)ferrocene)palladium(II) dichloride", NaN, NaN], [97.8741226196289, "C1COCCO1", "CC(=O)[O-].[K+]", "Reaxys Name (1,1'-bis(diphenylphosphino)ferrocene)palladium(II) dichloride", NaN, NaN], [95.84452819824219, "C1COCCO1", "[MgH2]", "Cl[Pd](Cl)([P](c1ccccc1)(c1ccccc1)c1ccccc1)[P](c1ccccc1)(c1ccccc1)c1ccccc1", NaN, NaN], [67.86063385009766, "C1CCOC1", "[MgH2]", "Cl[Pd](Cl)([P](c1ccccc1)(c1ccccc1)c1ccccc1)[P](c1ccccc1)(c1ccccc1)c1ccccc1", NaN, NaN]]""")
    for condition_list in condition_result:
        temperature, solvent, reagents, catalyst, _, _ = condition_list
        condition_part_img_list = []

        temperature_img = Image.new(pil_img_list[0].mode, (width_mol, height_each_img))  #
        draw = ImageDraw.Draw(temperature_img)
        draw.rectangle([(0, 0), temperature_img.size], fill=(255, 255, 255))
        text = "%s degrees Celsius" % (int(temperature))
        position = (0,100)  # 文字的起始位置 (x, y)
        font = ImageFont.truetype(font_file, 24)  # 使用指定字体和大小
        color = (0, 0, 0)  # 文字颜色，RGB 格式
        draw.text(position, text, font=font, fill=color)
        condition_part_img_list.append(temperature_img)

        for sth in (solvent, reagents, catalyst):
            mol = AllChem.MolFromSmiles(sth)
            if not mol:
                sth_img = Image.new(pil_img_list[0].mode, (width_mol, height_each_img))  #
                draw = ImageDraw.Draw(sth_img)
                draw.rectangle([(0, 0), sth_img.size], fill=(255,255,255))
                text=""
                for char_idx ,char in enumerate(sth):
                    if char_idx%20==0:
                        text+="\n"
                    text+=char
                position = (0,0)  # 文字的起始位置 (x, y)
                font = ImageFont.truetype(font_file, 24)  # 使用指定字体和大小
                color = (0,0,0)  # 文字颜色，RGB 格式
                draw.text(position, text, font=font, fill=color)
            else:
                sth_img = Draw.MolToImage(mol)
            condition_part_img_list.append(sth_img)

        # 创建一个空白画布，用于拼接condition图片
        condition_img = Image.new(pil_img_list[0].mode, (width, height_each_img))  #
        # 在画布上拼接图片
        for img_idx, img in enumerate(condition_part_img_list):
            condition_img.paste(img, (width_mol * img_idx, 0))

        pil_img_list.append(condition_img)

    # 创建一个空白画布，用于拼接图片
    result_width = width  # 图片拼接在一起
    result_height = height_each_img * len(pil_img_list)
    condition_img_result = Image.new(pil_img_list[0].mode, (result_width, result_height))  #
    # 在画布上拼接图片
    for img_idx, img in enumerate(pil_img_list):
        condition_img_result.paste(img, (0, height_each_img * img_idx))
    #result.show()
    return condition_img_result,condition_result


q = deque()
for molID in result_dict:
    os.system("mkdir %s/molecule_%s"%(output_dir,molID))
    for path_id, path_dict in enumerate(result_dict[molID]["paths"]): #广度遍历tree

        head = path_dict
        q.append(head)
        rxn_smiles_list = []
        while (len(q) != 0):
            point = q.popleft()
            if ">" in point["smiles"]:
                rxn_smiles_list.append(point["smiles"])
            for cp in point["children"]:
                q.append(cp)
        # print()

        if len(rxn_smiles_list) == 0:
            continue
        elif len(rxn_smiles_list) == 1:
            #condition prediction
            os.system("mkdir %s/molecule_%s/pathway_%s_%s_condition" % (output_dir, molID, molID, path_id))
            condition_img,condition_result=output_condiction_picture(rxn_smiles_list[0])
            condition_img.save("%s/molecule_%s/pathway_%s_%s_condition/rxn_0_condition.png" % (output_dir, molID, molID, path_id))

            rxn = AllChem.ReactionFromSmarts(rxn_smiles_list[0], useSmiles=True)
            img = Draw.ReactionToImage(rxn, subImgSize=(800, 300))
            img.save('%s/molecule_%s/pathway_%s_%s.png' % (output_dir,molID, molID, path_id))
            # img.show()
            # exit()
            # d2d = Draw.MolDraw2DCairo(800, 300)
            # d2d.DrawReaction(rxn)
            # png = d2d.GetDrawingText()
            # open('%s/result_%s_%s.jpg'%(tmp_dir,molID,path_id), 'wb+').write(png)



        else:
            pil_img_list = []
            width = 800
            height = 300
            width_mol = 200
            os.system("mkdir %s/molecule_%s/pathway_%s_%s_condition" % (output_dir, molID, molID, path_id))
            for rxn_idx, rxn_smiles in enumerate(reversed(rxn_smiles_list)):
                rxn = AllChem.ReactionFromSmarts(rxn_smiles, useSmiles=True)
                img = Draw.ReactionToImage(rxn, subImgSize=(width_mol, height))  # 每个分子的尺寸 反应箭头也按一个分子算
                img = img.resize((width, height))
                img.save("%s/tmp/tmp_%s_%s_%s.png" % (output_dir, molID, path_id, rxn_idx))
                # d2d = Draw.MolDraw2DCairo(800, 300)
                # d2d.DrawReaction(rxn)
                # png = d2d.GetDrawingText()
                # open("%s/tmp_%s_%s_%s.png"%(tmp_dir,molID,path_id,rxn_idx), 'wb+').write(png)
                # img=Draw.ReactionToImage(rxn,subImgSize=(200, 200))
                # img.save("./data/rxn_draw/%s_%s_%s.png"%(molID,path_id,rxn_idx))

                pil_img_list.append(img)

                # condition prediction
                condition_img,condition_result = output_condiction_picture(rxn_smiles)
                condition_img.save(
                    "%s/molecule_%s/pathway_%s_%s_condition/rxn_%s_condition.png" % (output_dir, molID, molID, path_id,rxn_idx))

            # 创建一个空白画布，用于拼接图片
            result_width = width  # 图片拼接在一起
            result_height = height * len(pil_img_list)
            result = Image.new(pil_img_list[0].mode, (result_width, result_height))  #

            # 在画布上拼接图片
            for img_idx, img in enumerate(pil_img_list):
                result.paste(img, (0, height * img_idx))

            # 保存拼接后的图片
            result.save('%s/molecule_%s/pathway_%s_%s.png' % (output_dir,molID, molID, path_id))
