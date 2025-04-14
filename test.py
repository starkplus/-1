import gradio as gr
from vector_search import OvarianCancerVectorSearch
import pandas as pd

# 初始化搜索系统
json_path = "D:/AAAlearnings/新建文件夹/learning/dian/智慧医疗组/获取网页信息学习/ovarian_cancer_data.json"
search_system = OvarianCancerVectorSearch(json_path)

def search_data(query, top_k):
    """执行搜索并返回结果"""
    results = search_system.search(query, top_k=int(top_k))
    
    # 构建结果表格
    data = []
    for res in results:
        data.append({
            "ID": res["id"],
            "标题": res["标题"],
            "年龄": res["年龄"],
            "病理类型": res["病理类型"],
            "既往治疗线数": res["既往治疗线数"],
            "ECOG": res["ECOG"],
            "相似度": f"{res['相似度']:.4f}",
        })
    
    # 构建详细信息
    details = ""
    if results:
        res = results[0]  # 取相似度最高的结果展示详细信息
        details = f"### 详细信息 (ID: {res['id']})\n\n"
        details += f"**链接**: {res['链接']}\n\n"
        details += f"**标题**: {res['标题']}\n\n"
        details += f"**纳入标准**:\n{res['纳入标准']}\n\n"
        details += f"**提取信息**:\n- 年龄: {res['年龄']}\n- 病理类型: {res['病理类型']}\n- 既往治疗线数: {res['既往治疗线数']}\n- ECOG: {res['ECOG']}"
    
    return pd.DataFrame(data), details

# 创建Gradio界面
with gr.Blocks(title="卵巢癌数据向量检索系统") as demo:
    gr.Markdown("# 卵巢癌临床试验数据向量检索系统")
    gr.Markdown("输入查询内容，包含年龄、病理类型、既往治疗线数、ECOG等信息")
    
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                label="查询内容", 
                placeholder="例如：年龄50-65岁，高级别浆液性卵巢癌，2线治疗，ECOG 0-1分",
                lines=3
            )
            top_k = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="返回结果数量")
            submit_btn = gr.Button("搜索")
        
        with gr.Column():
            example1 = gr.Examples(
                examples=[
                    ["年龄50-65岁，高级别浆液性卵巢癌，2线治疗，ECOG 0-1分"],
                    ["铂耐药复发卵巢癌，ECOG 0-2分"],
                    ["年龄小于65岁，上皮性卵巢癌，既往至少接受过2线治疗"],
                    ["年龄18-75岁，输卵管癌或原发性腹膜癌，ECOG 0分"],
                ],
                inputs=query_input,
            )
    
    results_table = gr.DataFrame(label="搜索结果")
    details_output = gr.Markdown(label="详细信息")
    
    submit_btn.click(
        fn=search_data,
        inputs=[query_input, top_k],
        outputs=[results_table, details_output]
    )

# 启动Gradio界面
if __name__ == "__main__":
    demo.launch()