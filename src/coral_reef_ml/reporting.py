"""Create the polished, concise two-page PDF write-up from measured results."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import mm
from .team_info import get_team_members
from .design_assets import prepare_design_assets

NAVY = HexColor('#102F3A')
TEAL = HexColor('#1B8A8F')
CORAL = HexColor('#F07861')
INK = HexColor('#22363E')
MUTED = HexColor('#60757D')
PALE = HexColor('#F5F8F8')
MINT = HexColor('#E1F3F0')
LINE = HexColor('#DCE7E9')
WHITE = colors.white
W, H = A4

STYLES = {
 'body': ParagraphStyle('body', fontName='Helvetica', fontSize=8.3, leading=11.4, textColor=INK, spaceAfter=0),
 'small': ParagraphStyle('small', fontName='Helvetica', fontSize=7.2, leading=9.2, textColor=MUTED),
 'tiny': ParagraphStyle('tiny', fontName='Helvetica', fontSize=6.6, leading=8.2, textColor=MUTED),
 'card': ParagraphStyle('card', fontName='Helvetica', fontSize=8.2, leading=10, textColor=MUTED),
 'table': ParagraphStyle('table', fontName='Helvetica', fontSize=7.1, leading=8.2, textColor=INK),
 'table_bold': ParagraphStyle('table_bold', fontName='Helvetica-Bold', fontSize=7.1, leading=8.2, textColor=INK),
 'table_header': ParagraphStyle('table_header', fontName='Helvetica-Bold', fontSize=7.1, leading=8.2, textColor=WHITE),
}


def _top_rect(c, x, top, width, height, fill, radius=0):
    c.setFillColor(fill); c.setStrokeColor(fill)
    y = H - top - height
    if radius: c.roundRect(x, y, width, height, radius, fill=1, stroke=0)
    else: c.rect(x, y, width, height, fill=1, stroke=0)


def _para(c, text, x, top, width, style=None, max_height=999):
    style = style or STYLES['body']
    p = Paragraph(text, style)
    _, height = p.wrap(width, max_height)
    p.drawOn(c, x, H-top-height)
    return top + height


def _section(c, label, x, top, width):
    c.setFillColor(TEAL); c.roundRect(x, H-top-11, 3, 11, 1.5, fill=1, stroke=0)
    _para(c, f'<b>{escape(label.upper())}</b>', x+8, top-1, width-8,
          ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=8.7, leading=10, textColor=NAVY))


def _footer(c, page):
    _top_rect(c, 34, 813, W-68, .7, LINE)
    _para(c, 'UE24CS352A | Machine Learning Mini-Project | Problem 79', 36, 818, 360, STYLES['tiny'])
    c.setFillColor(MUTED); c.setFont('Helvetica-Bold', 7); c.drawRightString(W-36, 17, f'{page} / 2')


def _metric(c, x, top, width, label, value, note, accent):
    _top_rect(c, x, top, width, 49, PALE, 6)
    _top_rect(c, x, top, 3, 49, accent, 1)
    _para(c, f'<b>{escape(label.upper())}</b>', x+10, top+7, width-16,
          ParagraphStyle('metric_label', fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=MUTED))
    _para(c, f'<b>{escape(value)}</b>', x+10, top+18, width-16,
          ParagraphStyle('metric_value', fontName='Helvetica-Bold', fontSize=17, leading=18, textColor=NAVY))
    _para(c, escape(note), x+10, top+37, width-16, STYLES['tiny'])


def generate_report(root: Path, cv_results, metrics, report_dict, importance, audit) -> Path:
    root = Path(root)
    out = root / 'results' / 'Coral_Reef_Mini_Project_Report.pdf'
    out.parent.mkdir(parents=True, exist_ok=True)
    assets = prepare_design_assets(root, cv_results, report_dict, importance, audit)
    team = get_team_members(root).replace('\n', '  |  ').replace('[Add both names]', 'Team names to be confirmed')
    c = canvas.Canvas(str(out), pagesize=A4, pageCompression=1)
    c.setTitle('Predicting Coral Reef Regimes from Human and Natural Influences')
    c.setAuthor(team)
    left, right = 36, W-36
    usable = right-left

    # PAGE 1 - question, data and protocol
    c.setFillColor(PALE); c.rect(0,0,W,H,fill=1,stroke=0)
    _top_rect(c, 0, 0, W, 128, NAVY)
    _top_rect(c, 0, 0, 7, 128, TEAL)
    _para(c, 'MACHINE LEARNING MINI-PROJECT  /  PROBLEM 79', left+3, 18, usable-10,
          ParagraphStyle('eyebrow', fontName='Helvetica-Bold', fontSize=7.6, leading=9, textColor=HexColor('#77DAD0')))
    _para(c, 'Predicting Coral Reef Regimes<br/>from Human and Natural Influences', left+3, 36, usable-16,
          ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=21, leading=24, textColor=WHITE))
    _para(c, f'UE24CS352A | Team: {escape(team)}', left+3, 91, usable-16,
          ParagraphStyle('subtitle', fontName='Helvetica', fontSize=8.3, leading=10, textColor=HexColor('#DAE7E9')))

    gap=8; mw=(usable-3*gap)/4
    cards=[('SITES',str(audit['rows']),'Hawaiian reef observations',TEAL),('PREDICTORS',str(audit['predictor_count']),'Human + biophysical',CORAL),('TRAIN',str(audit['train_rows']),'80% stratified split',TEAL),('HELD-OUT TEST',str(audit['test_rows']),'Used once after selection',CORAL)]
    for i,(lab,val,note,acc) in enumerate(cards): _metric(c,left+i*(mw+gap),145,mw,lab,val,note,acc)

    _section(c,'Research question',left,210,usable)
    _para(c, 'Can 20 anthropogenic and biophysical predictors classify a Hawaiian reef site into its observed regime label? This is supervised four-class classification using nominal labels <b>1, 2, 3 and 5</b>. It predicts the provided label; it does not establish that any predictor causes a regime transition.', left+10, 229, usable-18, STYLES['body'])

    # Two-column dataset and safeguards
    colgap=16; colw=(usable-colgap)/2
    _top_rect(c,left,278,colw,154,WHITE,7); _top_rect(c,left,278,colw,3,TEAL,1)
    _section(c,'Dataset & target',left+12,291,colw-20)
    data_txt=(f'<b>Source:</b> Hawaii_RegimesPredictors.txt<br/>'
              f'<b>Rows:</b> {audit["rows"]}; <b>inputs:</b> {audit["predictor_count"]}<br/>'
              f'<b>Predictors:</b> Effluent through Depth<br/>'
              f'<b>Class counts:</b> 1: {audit["class_counts"]["1"]}; 2: {audit["class_counts"]["2"]}; 3: {audit["class_counts"]["3"]}; 5: {audit["class_counts"]["5"]}<br/>'
              f'<b>Exact duplicate rows:</b> {audit["exact_duplicate_rows_in_source"]}; none removed automatically.')
    _para(c,data_txt,left+12,313,colw-24,STYLES['body'])
    x2=left+colw+colgap
    _top_rect(c,x2,278,colw,154,WHITE,7); _top_rect(c,x2,278,colw,3,CORAL,1)
    _section(c,'Leakage safeguards',x2+12,291,colw-20)
    safeguards=('Excluded: Regime1/2/3/5 target one-hot fields, ecological response variables, IDs and coordinates.<br/>'
                '<br/><b>Missingness:</b> Complexity 113 values; Depth 12 values.<br/>'
                '<b>Imputation:</b> median imputation inside each pipeline / training fold.<br/>'
                '<b>Split:</b> random_state=42; 496 train / 124 test.')
    _para(c,safeguards,x2+12,313,colw-24,STYLES['body'])

    _section(c,'Evaluation design',left,454,usable)
    flow_y=479; flow_gap=7; floww=(usable-4*flow_gap)/5
    flow=[('01','Audit','Validate schema'),('02','Split','Stratified 80/20'),('03','Compare','5-fold training CV'),('04','Select','Mean macro-F1'),('05','Test','Held-out evaluation')]
    for i,(n,head,desc) in enumerate(flow):
        xx=left+i*(floww+flow_gap)
        _top_rect(c,xx,flow_y,floww,57,WHITE,5)
        _para(c,f'<b>{n}</b>',xx+7,flow_y+6,floww-12,ParagraphStyle('stepn',fontName='Helvetica-Bold',fontSize=7,leading=8,textColor=CORAL))
        _para(c,f'<b>{head}</b>',xx+7,flow_y+18,floww-12,ParagraphStyle('steph',fontName='Helvetica-Bold',fontSize=8,leading=9,textColor=NAVY))
        _para(c,desc,xx+7,flow_y+31,floww-12,ParagraphStyle('stepd',fontName='Helvetica',fontSize=6.5,leading=8,textColor=MUTED))

    _section(c,'Models compared',left,552,usable)
    models='Most-frequent baseline; class-weighted Logistic Regression; RBF SVM; Random Forest; Gradient Boosting; and Random Forest plus five interaction features. The selected model is chosen only from training-set cross-validation; the held-out test set is reserved for final evaluation.'
    _para(c,models,left+10,571,usable-18,STYLES['body'])
    _top_rect(c,left,638,usable,82,MINT,7)
    _para(c,'<b>Evaluation choice:</b> macro-F1 gives equal weight to each class F1, making it useful when class-level performance matters. Accuracy, balanced accuracy, micro-F1, weighted-F1 and per-class results are also reported.',left+13,652,usable-26,
          ParagraphStyle('callout',fontName='Helvetica',fontSize=8.2,leading=11,textColor=NAVY))
    _para(c,'Scope note: this is an adapted, reproducible implementation of the assigned problem, not an exact reproduction of every experiment in the Stanford reference project.',left+2,741,usable-4,STYLES['small'])
    _footer(c,1); c.showPage()

    # PAGE 2 - results, charts and interpretation
    c.setFillColor(PALE); c.rect(0,0,W,H,fill=1,stroke=0)
    _top_rect(c,0,0,W,72,NAVY); _top_rect(c,0,0,7,72,TEAL)
    _para(c,'RESULTS & INTERPRETATION',left+3,15,usable-16,
          ParagraphStyle('eyebrow2',fontName='Helvetica-Bold',fontSize=7.5,leading=9,textColor=HexColor('#77DAD0')))
    _para(c,'Random Forest led cross-validation and held-out evaluation',left+3,31,usable-16,
          ParagraphStyle('title2',fontName='Helvetica-Bold',fontSize=15,leading=19,textColor=WHITE))

    gap=8; mw=(usable-2*gap)/3
    _metric(c,left,86,mw,'BEST CV MACRO-F1',f'{cv_results.iloc[0]["cv_macro_f1_mean"]:.3f}',f'{cv_results.iloc[0]["model"]}; mean across 5 folds',TEAL)
    _metric(c,left+mw+gap,86,mw,'TEST MACRO-F1',f'{metrics["test_macro_f1"]:.3f}',f'n = {metrics["test_rows"]}; held-out split',CORAL)
    _metric(c,left+2*(mw+gap),86,mw,'TEST ACCURACY',f'{metrics["test_accuracy"]:.3f}',f'{int(round(metrics["test_accuracy"]*metrics["test_rows"]))} of {metrics["test_rows"]} correct',TEAL)

    _section(c,'Training-only cross-validation comparison',left,151,usable)
    # Draw table using paragraph cells so labels wrap neatly.
    headers=['Model','Input features','Macro-F1 mean','Fold SD','Balanced acc.','Accuracy']
    rows=[]
    for h in headers: rows.append(None)
    table_data=[[Paragraph(f'<b>{escape(h)}</b>', STYLES['table_header']) for h in headers]]
    for _,r in cv_results.iterrows():
        feat = '-' if 'Baseline' in str(r['model']) or 'Most-Frequent' in str(r['model']) else str(int(r['feature_count']))
        vals=[str(r['model']),feat,f"{r['cv_macro_f1_mean']:.3f}",f"{r['cv_macro_f1_std']:.3f}",f"{r['cv_balanced_accuracy_mean']:.3f}",f"{r['cv_accuracy_mean']:.3f}"]
        table_data.append([Paragraph(escape(vals[0]),STYLES['table'])]+[Paragraph(escape(v),STYLES['table']) for v in vals[1:]])
    widths=[62*mm,22*mm,23*mm,17*mm,26*mm,23*mm]
    tbl=Table(table_data,colWidths=widths,rowHeights=[19]+[18]*len(cv_results))
    tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),WHITE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,PALE]),('GRID',(0,0),(-1,-1),.35,LINE),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('ALIGN',(1,1),(-1,-1),'CENTER'),('FONTNAME',(0,1),(0,1),'Helvetica-Bold'),
        ('BACKGROUND',(0,1),(-1,1),MINT),
    ]))
    tw,th=tbl.wrapOn(c,usable,400); tbl.drawOn(c,left,H-168-th)
    y_after=168+th
    _para(c,'Model selection uses only training-set CV macro-F1. The interaction ablation (0.687) did not outperform the base Random Forest (0.692).',left+2,y_after+7,usable-4,STYLES['small'])

    # Charts row
    chart_top=y_after+32
    _top_rect(c,left,chart_top,usable,180,WHITE,6)
    _para(c,'<b>CROSS-VALIDATION</b>',left+10,chart_top+9,usable/2-12,
          ParagraphStyle('charthead1',fontName='Helvetica-Bold',fontSize=7.2,leading=9,textColor=TEAL))
    _para(c,'<b>HELD-OUT TEST</b>',left+usable/2+5,chart_top+9,usable/2-14,
          ParagraphStyle('charthead2',fontName='Helvetica-Bold',fontSize=7.2,leading=9,textColor=TEAL))
    c.drawImage(str(assets['cv']),left+6,H-chart_top-165,width=usable/2-17,height=145,preserveAspectRatio=True,anchor='c',mask='auto')
    c.drawImage(str(assets['cm']),left+usable/2+15,H-chart_top-164,width=usable/2-29,height=142,preserveAspectRatio=True,anchor='c',mask='auto')

    lower_top=chart_top+194
    # class metrics and top features, left column
    colgap=14; colw=(usable-colgap)/2; x2=left+colw+colgap
    _top_rect(c,left,lower_top,colw,119,WHITE,6)
    _section(c,'Class-wise recall',left+10,lower_top+11,colw-18)
    # row-level per class metrics from classification report
    for i,lab in enumerate(['1','2','3','5']):
        r=report_dict[report_dict.iloc[:,0].astype(str)==lab]
        rec=float(r['recall'].iloc[0]) if not r.empty and 'recall' in r.columns else 0
        f1=float(r['f1-score'].iloc[0]) if not r.empty and 'f1-score' in r.columns else 0
        y=lower_top+31+i*19
        _para(c,f'<b>Regime {lab}</b>',left+12,y,43,ParagraphStyle('clab',fontName='Helvetica-Bold',fontSize=7.1,leading=8,textColor=NAVY))
        _para(c,f'Recall {rec:.3f}   |   F1 {f1:.3f}',left+59,y,colw-70,ParagraphStyle('cval',fontName='Helvetica',fontSize=7.1,leading=8,textColor=INK))
    _top_rect(c,x2,lower_top,colw,119,WHITE,6)
    _section(c,'Top permutation-importance features',x2+10,lower_top+11,colw-18)
    top_feats=importance.sort_values('permutation_importance_mean',ascending=False).head(3)
    for i,(_,r) in enumerate(top_feats.iterrows()):
        y=lower_top+33+i*23
        _para(c,f'<b>{i+1}. {escape(str(r["feature"]))}</b>',x2+12,y,colw-24,ParagraphStyle(f'feat{i}',fontName='Helvetica-Bold',fontSize=7.1,leading=8,textColor=NAVY))
        _para(c,f'Mean macro-F1 decrease when shuffled: {float(r["permutation_importance_mean"]):.3f}',x2+12,y+10,colw-24,STYLES['tiny'])

    # limitations and references as small footer block
    note_top=lower_top+130
    _top_rect(c,left,note_top,usable,48,MINT,6)
    _para(c,'<b>Limitations:</b> the sample is modest and restricted to Hawaii; regime 4 is absent in the provided subset; the model has not been validated on independent geographic data. Permutation importance is descriptive, not causal.',left+10,note_top+9,usable-20,
          ParagraphStyle('limits',fontName='Helvetica',fontSize=7.4,leading=9.2,textColor=NAVY))
    ref_top=note_top+57
    refs=('References: Jouffray et al. (2019), <i>Parsing human and biophysical drivers of coral reef regimes</i>, Proc. R. Soc. B 286:20182544, https://doi.org/10.1098/rspb.2018.2544; Stanford CS229 project: https://cs229.stanford.edu/proj2019spr/report/56.pdf; data: https://github.com/JBjouffray/Hawaii_RegimesPredictors.')
    _para(c,refs,left+2,ref_top,usable-4,STYLES['tiny'])
    _footer(c,2); c.save()
    return out
