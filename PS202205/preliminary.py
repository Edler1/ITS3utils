#!/bin/env python3

# Plot preliminary results for approval

import plot_util
import ROOT
from copy import deepcopy
from pprint import pprint
import datetime

# Binning: width, min, max
database = {
  'submatrix': ['AC','DC','SF'],
  'variant': ['B4', 'A4'],
  'A4':{
    'template': 'B4',
    'process': 'std',
    'binning_seedChargeENC':[50, 0, 3100],
    'noise':'qa/PS-A4_HV10-noisemap.root',
    'AC':{
      'calibration': 4.167,
      'result':{
        'file': 'output/analysisCE65-AC_cls1000snr3sum3x3_PS-A4_HV10.root',
      },
    },
    'DC':{
      'calibration': 5.556,
      'result':{
        'file': 'output/analysisCE65-DC_cls1200snr2sum3x3_PS-A4_HV10.root',
      },
    },
    'SF':{
      'calibration': 1.493,
      'result':{
        'file': 'output/analysisCE65-SF_cls300snr2sum3x3_PS-A4_HV10.root',
      },
    },
  },
  'B4_HV1':{
    'template': 'B4',
    'noise':'qa/PS-B4_HV1-noisemap.root',
    'setup':{
      'HV': 1,
      'PWELL': 0,
      'PSUB': 0,
    },
  },
  'B4':{
    'template': 'B4',
    'PIXEL_NX': 64,
    'PIXEL_NY': 32,
    'process': 'mod_gap',
    'split': 4,
    'setup':{
      'HV': 10,
      'PWELL': 0,
      'PSUB': 0,
    },
    'binning_noiseENC':[1.0, 0, 100],
    'binning_chargeENC':[50, 0, 5100],
    'binning_seedChargeENC':[50, 0, 3100],
    'noise':'qa/PS-B4_HV10-noisemap.root',
    'AC':{
      'title': 'AC amp.',
      'edge':[0, 20],
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'calibration': 4.348,
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-AC_cls500snr3sum3x3_PS-B4_HV10.root',
      }
    },
    'DC':{
      'title': 'DC amp.',
      'edge':[21, 41],
      'calibration': 3.704,
      'binning_noise':[5, 0, 400],
      'binning_charge':[100, 0, 15000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-DC_cls1000snr3sum3x3_PS-B4_HV10.root',
      }
    },
    'SF':{
      'title': 'SF',
      'edge':[42, 63],
      'calibration': 1.205,
      'binning_noise':[1, 0, 100],
      'binning_charge':[50, 0, 5000],
      'result':{
        'seed_snr': 3,
        'seed_charge': 200,
        'cluster_charge': 1000,
        'file':'output/analysisCE65-SF_cls200snr3sum3x3_PS-B4_HV10.root',
      }
    },
  }
}
def dict_update(config : dict, template : dict):
  configNew = deepcopy(template)
  for k, v in config.items():
    if(type(v) is dict):
      configNew[k] = dict_update(v, template[k])
    else:
      configNew[k] = deepcopy(v)
  return configNew
for chip in database['variant']:
  chipConfig = database[chip]
  if(chip == chipConfig.get('template')): continue
  database[chip] = dict_update(chipConfig, database[chipConfig['template']])

# Style
HIST_Y_SCALE = 1.4
color_vars = {}
plot_util.COLOR_SET = plot_util.COLOR_SET_ALICE
for sub in database['submatrix']:
  color_vars[sub] = next(plot_util.COLOR)
marker_vars = {}
line_vars = {}
plot_util.MARKER_SET = plot_util.MARKER_SET_DEFAULT
for chips in database['variant']:
  marker_vars[chips] = next(plot_util.MARKER)
  line_vars[chips] = next(plot_util.LINE)

def plot_alice(painter : plot_util.Painter, x1 = 0.02, y1 = 0.03, x2 = 0.47, y2 = 0.17,
 size=0.04, pos='lt'):
  """
  """
  label = painter.new_obj(plot_util.InitALICELabel(x1, y1, x2, y2, 
    align=12, type='#bf{ALICE ITS3-WP3} beam test #it{preliminiary}', pos=pos))
  painter.add_text(label, 'Beam test @CERN-PS May 2022, 10 GeV/#it{c} #pi^{-}', size=0.03)
  painter.add_text(label, datetime.datetime.now().strftime("Plotted on %d %b %Y"), size=0.03)
  label.Draw('same')
  return label

# Noise
def plot_noise(painter : plot_util.Painter, variant='B4'):
  """Noise distribution of each sub-matrix
  """
  painter.NextPad()
  painter.pageName = f'Noise - {variant}'
  chip_vars = database[variant]
  chip_setup = chip_vars['setup']
  noiseFile = ROOT.TFile.Open(chip_vars['noise'])
  hNoiseMap = noiseFile.Get('hnoisepl1')
  lgd = painter.new_obj(ROOT.TLegend(0.75, 0.55, 0.90, 0.7))
  histMax = 0
  for sub in database['submatrix']:
    vars = chip_vars[sub]
    hsub = painter.new_hist(f'hnoise_{chip}_{sub}','Noise Distribution;Equivalent Noise Charge (#it{e^{-}});# Pixels',
      chip_vars['binning_noiseENC'])
    hsub.SetLineColor(color_vars[sub])
    hsub.SetLineWidth(2)
    hsub.SetMarkerStyle(marker_vars[chip])
    hsub.SetMarkerColor(color_vars[sub])
    lgd.AddEntry(hsub,vars['title'])
    for ix in range(vars['edge'][0], vars['edge'][1]+1):
      for iy in range(chip_vars['PIXEL_NY']):
        hsub.Fill(hNoiseMap.GetBinContent(ix+1,iy+1) / vars['calibration'])
    if(hsub.GetMaximum() > histMax):
      histMax = hsub.GetMaximum()
    painter.DrawHist(hsub, samePad=True)
  painter.primaryHist.GetYaxis().SetRangeUser(0, HIST_Y_SCALE * histMax)
  ROOT.gPad.SetLogy(False)
  # Legend
  lgd.Draw('same')
  # Text
  plot_alice(painter)
  ptxt = painter.draw_text(0.65, 0.75, 0.95, 0.92)
  painter.add_text(ptxt, f'Chip : CE65 (MLR1)')
  painter.add_text(ptxt, f'Process : {chip_vars["process"]} (split {chip_vars["split"]})')
  painter.add_text(ptxt,
    f'HV-AC = {chip_setup["HV"]}, V_{{psub}} = {chip_setup["PSUB"]}, V_{{pwell}} = {chip_setup["PWELL"]} (V)',
    size=0.03)
  ptxt.Draw('same')
  painter.NextPage()

def plot_cluster_charge(painter : plot_util.Painter, optNorm=False, optSeed=False):
  """Cluster charge plot for all variants and sub-matrix
  """
  if(optSeed):
    painter.pageName = 'Seed Charge'
    histNameSource = 'seedChargeAssociated'
    histNameCharge = 'hSeedChargeENC'
    histNameRaw = 'hSeedCharge'
    histXTitle = 'Seed Charge'
    binningCharge = 'binning_seedChargeENC'
  else:
    painter.pageName = 'Cluster Charge'
    histNameSource = 'clusterChargeAssociated'
    histNameCharge = 'hClusterChargeENC'
    histNameRaw = 'hClusterCharge'
    histXTitle = 'Cluster Charge'
    binningCharge = 'binning_chargeENC'
  if optNorm:
    ROOT.gPad.SetTopMargin(0.05)
  histMax = 0
  lgd = painter.new_obj(ROOT.TLegend(0.60, 0.3, 0.90, 0.6))
  for chip in database['variant']:
    chip_vars = database[chip]
    for sub in database['submatrix']:
      sub_vars = chip_vars[sub]
      corry_vars = sub_vars['result']
      resultFile = ROOT.TFile.Open(corry_vars['file'])
      dirAna = resultFile.Get('AnalysisCE65')
      dirAna = dirAna.Get('CE65_4')
      hChargeRaw = painter.new_obj(dirAna.Get(histNameSource).Clone(f'{histNameRaw}_{chip}_{sub}'))
      hChargeRaw.SetDirectory(0x0)
      histName = f'{histNameCharge}_{chip}_{sub}'
      if optNorm:
        histName = f'{histNameCharge}norm_{chip}_{sub}'
      hCharge = painter.new_hist(histName,
        f'{histXTitle};{histXTitle} '+'(#it{e^{-}});Entries;',
        chip_vars[binningCharge])
      hCharge.SetBit(ROOT.TH1.kIsNotW)
      hCharge.GetYaxis().SetMaxDigits(4)
      hCharge.SetLineColor(color_vars[sub])
      hCharge.SetLineStyle(line_vars[chip])
      hCharge.SetMarkerColor(color_vars[sub])
      hCharge.SetMarkerStyle(marker_vars[chip])
      hCharge.SetMarkerSize(1.5)
      hCharge.SetDirectory(0x0)
      # Scale with calibration
      scale = sub_vars['calibration']
      binmin = hChargeRaw.FindBin(chip_vars[binningCharge][1] * scale)
      binmax = hChargeRaw.FindBin(chip_vars[binningCharge][2] * scale)
      for ix in range(binmin, binmax):
        calibratedX = hChargeRaw.GetBinCenter(ix) / scale
        val = hChargeRaw.GetBinContent(ix)
        hCharge.Fill(calibratedX, val)
      hCharge.Sumw2()
      if(optNorm):
        hCharge.Scale(1/hCharge.Integral('width'))
        hCharge.SetYTitle(f'Entries (normalised)')
      else:
        hCharge.SetYTitle(f'Entries / {hCharge.GetBinWidth(1):.0f} ' + '#it{e^{-}}')
      if(hCharge.GetMaximum() > histMax):
        histMax = hCharge.GetMaximum()
      painter.hist_rebin(hChargeRaw, sub_vars['binning_charge'])
      # Draw
      painter.DrawHist(hCharge, samePad=True)
        # Fitting
      fit, result = painter.optimise_hist_langau(hCharge,
        color=color_vars[sub], style=line_vars[chip], notext=True)
      result.Print() # DEBUG
        # Legend
      lgd.AddEntry(hCharge, f'{chip_vars["process"]} {sub_vars["title"]}'
        f' (SNR_{{seed}}>{corry_vars["seed_snr"]})')
      resultFile.Close()
  painter.primaryHist.GetYaxis().SetRangeUser(0, HIST_Y_SCALE * histMax)
  # Text
  painter.draw_text(0.60, 0.6, 0.90, 0.65, 'Fitting by Landau-Gaussian function', size=0.03, font=42).Draw('same')
  lgd.SetTextSize(0.035)
  lgd.Draw('same')
  plot_alice(painter)
  ptxt = painter.draw_text(0.62, 0.75, 0.95, 0.92)
  painter.add_text(ptxt, f'Chip : CE65 (MLR1)')
  painter.add_text(ptxt, f'Process : std/mod_gap (split {chip_vars["split"]})')
  chip_setup = chip_vars['setup']
  painter.add_text(ptxt,
    f'HV-AC = {chip_setup["HV"]}, V_{{psub}} = {chip_setup["PSUB"]}, V_{{pwell}} = {chip_setup["PWELL"]} (V)',
    size=0.03)
  ptxt.Draw('same')
  painter.NextPage()

def plot_seed_charge(painter : plot_util.Painter, optNorm=False):
  return plot_cluster_charge(painter, optSeed=True, optNorm=optNorm)

def plot_cluster_shape(painter : plot_util.Painter):
  """
  """
  sub = 'SF'
  for chip in database['variant']:
    lgd = painter.new_legend(0.65, 0.35, 0.95, 0.40)
    painter.pageName = f'ClusterShape - {chip}_{sub}'
    chip_vars = database[chip]
    chip_setup = chip_vars['setup']
    sub_vars = chip_vars[sub]
    corry_vars = sub_vars['result']
    resultFile = ROOT.TFile.Open(corry_vars['file'])
    dirAna = resultFile.Get('AnalysisCE65')
    dirAna = dirAna.Get('CE65_4')
    dirCluster = dirAna.Get('cluster')
    hRatio = painter.new_obj(dirCluster.Get("clusterChargeRatio").Clone(f'hClusterChargeRatio_{chip}_{sub}'))
    hRatio.UseCurrentStyle()
    hRatio.SetXTitle('#it{R}_{n} (#sum highest N pixels)')
    hRatio.SetYTitle('Accumulated charge ratio')
    hRatio.RebinY(int(0.02 // hRatio.GetYaxis().GetBinWidth(1) ))
    hRatio.GetXaxis().SetRangeUser(0,10)
    hRatio.GetYaxis().SetRangeUser(0,1.2)
    hPx = painter.new_obj(hRatio.ProfileX())
    hPx.SetLineColor(ROOT.kBlack)
    hPx.SetLineStyle(ROOT.kDashed) # dash-dot
    hPx.SetLineWidth(4)
    hPx.SetMarkerColor(ROOT.kBlack)
    hPx.SetMarkerStyle(plot_util.kFullStar)
    hPx.SetMarkerSize(4)
    painter.DrawHist(hRatio, option='colz', optNormY=True)
    hPx.Draw('same')
    lgd.AddEntry(hPx, '<#it{R}_{n}> (average)')
    lgd.Draw('same')
    # Label
    plot_alice(painter, pos='rb')
    # Text info
    ptxt = painter.draw_text(0.65, 0.45, 0.95, 0.65)
    painter.add_text(ptxt, f'Chip : CE65 (MLR1)')
    painter.add_text(ptxt, f'Process : {chip_vars["process"]} (split {chip_vars["split"]})')
    painter.add_text(ptxt,
      f'V_{{psub}} = {chip_setup["PSUB"]}, V_{{pwell}} = {chip_setup["PWELL"]} (V)',
      size=0.03)
    painter.add_text(ptxt,f'Sub-matrix : {sub}')
    ptxt.Draw('same')
    painter.NextPage()
  # Draw
def plot_tracking_residual(painter):
  """
  """

def plot_preliminary():
  plot_util.ALICEStyle()
  painter = plot_util.Painter(
    printer='preliminary.pdf',
    winX=1600, winY=1000, nx=1, ny=1)
  painter.PrintCover('CE65 Preliminary')
  plot_noise(painter,'B4')
  plot_noise(painter,'A4')
  plot_cluster_charge(painter)
  plot_cluster_charge(painter, optNorm=True)
  plot_seed_charge(painter)
  plot_seed_charge(painter, optNorm=True)
  plot_cluster_shape(painter)
  painter.PrintBackCover('-')

if __name__ == '__main__':
  plot_preliminary()
  #pprint(database)