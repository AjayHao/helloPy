from pyquery import PyQuery as pq

m = '''
<table class="tableForm" border="1">
<tbody><tr valign="top"><td class="Title" style="width:25%" width="223" valign="middle">重要合同</td><td width="223" valign="middle">否</td><td class="Title" width="223" valign="middle">重要合同备注</td><td width="223" valign="middle"></td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle">项目类型</td><td width="223" valign="middle"><span id="TxHmpd2_2">资产托管业务</span></td><td class="Title" width="223" valign="middle">协议类型</td><td width="223" valign="middle">证券经纪服务协议<span id="TxXylx2" style="display:none">证券经纪服务协议</span></td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle"><div id="TRYsbh3" style="display:none">预算编号</div>
<div id="TRYsbh5" style="display:none"><font color="#FF0000">注：合同原件移交法律部前请务必保存合同电子扫描件</font><div></div></div></td><td width="223" valign="middle"><div id="TRYsbh4" style="display:none"></div></td><td class="title" width="223" valign="middle"><div id="TRQbbh1" style="display:none">工作签报文件编号</div></td><td width="223" valign="middle"><div id="TRQbbh2" style="display:none"></div></td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle">对方当事人全称</td><td width="668" colspan="3" valign="middle">光道资产管理有限公司、中信建投证券股份有限公司&nbsp;&nbsp;
</td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle">合同金额</td><td width="223" valign="middle"><font size="2" face="宋体" id="IDHTJE"> 不适用 </font></td><td class="Title" width="223" valign="middle"><div align="center">合同格式</div></td><td width="223" valign="middle"><font face="宋体">非标准协议</font><span id="TxHtgs2" style="display:none">非标准协议</span></td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle">合同概要</td><td width="668" colspan="3" valign="middle">根据【总部合同[2020]第1015号、光道和盛7号私募证券投资基金-证券经纪服务协议（中信建投证券）】版本上仅修改了基金名称。烦请审核！</td></tr>

<tr valign="top"><td class="Title" width="223" rowspan="2" valign="middle">盖章类型</td><td width="223" valign="middle">B
<br>
<span id="TxGzlx2" style="display:none">B</span></td><td width="445" colspan="2" valign="middle"><font color="#8F8F8F">A类：对方已盖章、我方盖章生效合同</font><br>
<font color="#8F8F8F">B类：对方尚未盖章、我方先盖章合同</font></td></tr>

<tr valign="top"><td width="668" colspan="3" valign="middle">孟祥宁/资产托管部/GTJA于2020-04-10 14:05:21选择盖章类型为‘B’类，并已确认承诺：报审部门确认以我司先盖章合同为最终合同。</td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle"><font color="#FF0000">合同提交前是否已履行</font></td><td width="668" colspan="3" valign="middle">否  
</td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle"><font color="#FF0000">合同原件是否需要移交法律部</font></td><td width="668" colspan="3" valign="middle">是</td></tr>

<tr valign="top"><td class="Title" width="223" valign="middle">备注</td><td width="668" colspan="3" valign="middle"><br>

<br>
<span id="fzjg" style="display:none">
<br>
<table width="100%">
<tbody><tr><td width="80">回寄地址：</td><td></td></tr>
<tr><td width="80">邮编：</td><td></td></tr>
<tr><td width="80">收件人：</td><td></td></tr>
<tr><td width="80">联系电话：</td><td></td></tr>
</tbody></table>
</span></td></tr>

<tr valign="top"><td class="Title" width="223"><img width="1" height="1" src="/icons/ecblank.gif" border="0" alt=""></td><td width="668" colspan="3" valign="middle"><img width="1" height="1" src="/icons/ecblank.gif" border="0" alt=""></td></tr>
</tbody></table>
'''

htmlobj = pq(m)
tds = htmlobj('table.tableForm tr td').items()
for td in tds:
    if td.text() == '协议类型':
        print(td.next().remove('span').text())

    # 因对方当事人名称字段可能被页面吞掉，改为td:合同金额往前追溯
    if td.text() == '合同金额':
        print(td.parent().prev().find('td.Title').next().text().strip())
        break
