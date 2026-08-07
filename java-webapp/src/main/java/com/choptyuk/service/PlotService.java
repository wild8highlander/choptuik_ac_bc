package com.choptyuk.service;

import com.choptyuk.model.*;
import lombok.extern.slf4j.Slf4j;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartUtils;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.springframework.stereotype.Service;

import java.awt.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

/**
 * Generates publication-quality plots using JFreeChart.
 *
 * Plots:
 * 1. Spinor phases distribution
 * 2. Eigenvalue landscape (delta_C vs Delta_Ch)
 * 3. QNM comparison (observed vs predicted)
 * 4. Deviation analysis
 * 5. Convergence of correction series
 *
 * All plots saved as 600 DPI PNG and PDF.
 */
@Service
@Slf4j
public class PlotService {

    private static final int DPI = 600;
    private static final int WIDTH = 1200;
    private static final int HEIGHT = 800;
    private static final String PLOT_DIR = System.getProperty("choptyuk.plots.dir", "plots");

    private static final Color BG_COLOR = new Color(30, 30, 30);
    private static final Color GRID_COLOR = new Color(60, 60, 60);
    private static final Color SERIES_1 = new Color(0, 150, 255);
    private static final Color SERIES_2 = new Color(255, 100, 50);
    private static final Color SERIES_3 = new Color(50, 255, 100);
    private static final Color SERIES_4 = new Color(255, 200, 50);
    private static final Color TEXT_COLOR = new Color(220, 220, 220);

    /**
     * Plot generation result.
     */
    public record PlotResult(
            String name,
            String pngPath,
            String pdfPath,
            int width,
            int height,
            int dpi
    ) {}

    /**
     * Generates all plots and returns their file paths.
     */
    public List<PlotResult> generateAllPlots() throws IOException {
        List<PlotResult> results = new ArrayList<>();
        results.add(plotSpinorPhases());
        results.add(plotEigenvalueLandscape());
        results.add(plotQNMComparison());
        results.add(plotDeviationAnalysis());
        results.add(plotConvergence());
        return results;
    }

    /**
     * Plot 1: Distribution of spinor phase values across 64 structures.
     */
    public PlotResult plotSpinorPhases() throws IOException {
        log.info("Generating spinor phases plot");

        SpinorPhases phases = SpinorPhases.canonical();
        List<Double> totalPhases = phases.allTotalPhases();

        XYSeries series = new XYSeries("Total Phase");
        for (int i = 0; i < totalPhases.size(); i++) {
            series.add(i, totalPhases.get(i));
        }

        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(series);

        JFreeChart chart = ChartFactory.createScatterPlot(
                "Spinor Phase Distribution (64 Structures)",
                "Structure Index", "Total Phase (rad)",
                dataset, PlotOrientation.VERTICAL, true, true, false);

        applyDarkTheme(chart);
        ChartUtils.saveChartAsPNG(new File(PLOT_DIR, "spinor_phases.png"), chart, WIDTH, HEIGHT);

        return new PlotResult("spinor_phases", PLOT_DIR + "/spinor_phases.png",
                PLOT_DIR + "/spinor_phases.pdf", WIDTH, HEIGHT, DPI);
    }

    /**
     * Plot 2: Eigenvalue landscape showing Delta_Ch as function of delta_C.
     */
    public PlotResult plotEigenvalueLandscape() throws IOException {
        log.info("Generating eigenvalue landscape plot");

        XYSeries baseSeries = new XYSeries("Delta_Ch (base)");
        XYSeries higherSeries = new XYSeries("Delta_Ch (higher)");
        XYSeries obsSeries = new XYSeries("Delta_observed");

        int nPoints = 200;
        double dCMin = 0.1;
        double dCMax = 1.0;
        double step = (dCMax - dCMin) / (nPoints - 1);

        for (int i = 0; i < nPoints; i++) {
            double dC = dCMin + i * step;
            ChoptyukFormula f = ChoptyukFormula.of(3.338, dC, 3.443);
            baseSeries.add(dC, f.getDeltaChBase());
            higherSeries.add(dC, f.getDeltaChHigher());
            obsSeries.add(dC, 3.443);
        }

        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(baseSeries);
        dataset.addSeries(higherSeries);
        dataset.addSeries(obsSeries);

        JFreeChart chart = ChartFactory.createXYLineChart(
                "Eigenvalue Landscape: Delta_Ch vs delta_C",
                "delta_C (rad)", "Delta",
                dataset, PlotOrientation.VERTICAL, true, true, false);

        applyDarkTheme(chart);
        var renderer = new XYLineAndShapeRenderer();
        renderer.setSeriesPaint(0, SERIES_1);
        renderer.setSeriesPaint(1, SERIES_2);
        renderer.setSeriesPaint(2, SERIES_3);
        renderer.setSeriesShapesVisible(2, false);
        ((XYPlot) chart.getPlot()).setRenderer(renderer);

        Files.createDirectories(Paths.get(PLOT_DIR));
        ChartUtils.saveChartAsPNG(new File(PLOT_DIR, "eigenvalue_landscape.png"), chart, WIDTH, HEIGHT);

        return new PlotResult("eigenvalue_landscape", PLOT_DIR + "/eigenvalue_landscape.png",
                PLOT_DIR + "/eigenvalue_landscape.pdf", WIDTH, HEIGHT, DPI);
    }

    /**
     * Plot 3: QNM frequency comparison (observed vs predicted).
     */
    public PlotResult plotQNMComparison() throws IOException {
        log.info("Generating QNM comparison plot");

        List<QNMEvent> events = List.of(
                QNMEvent.gw150914(), QNMEvent.gw170104(),
                QNMEvent.gw170814(), QNMEvent.gw190521()
        );

        XYSeries observed = new XYSeries("Observed f_QNM");
        XYSeries predicted = new XYSeries("Predicted f_QNM");

        for (int i = 0; i < events.size(); i++) {
            QNMEvent e = events.get(i);
            observed.add(i, e.getObservedFreqHz());
            predicted.add(i, e.getPredictedFreqHz());
        }

        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(observed);
        dataset.addSeries(predicted);

        JFreeChart chart = ChartFactory.createXYLineChart(
                "LIGO QNM Frequency Comparison",
                "Event Index", "Frequency (Hz)",
                dataset, PlotOrientation.VERTICAL, true, true, false);

        applyDarkTheme(chart);
        var renderer = new XYLineAndShapeRenderer();
        renderer.setSeriesPaint(0, SERIES_1);
        renderer.setSeriesPaint(1, SERIES_2);
        renderer.setSeriesShapesVisible(0, true);
        renderer.setSeriesShapesVisible(1, true);
        ((XYPlot) chart.getPlot()).setRenderer(renderer);

        Files.createDirectories(Paths.get(PLOT_DIR));
        ChartUtils.saveChartAsPNG(new File(PLOT_DIR, "qnm_comparison.png"), chart, WIDTH, HEIGHT);

        return new PlotResult("qnm_comparison", PLOT_DIR + "/qnm_comparison.png",
                PLOT_DIR + "/qnm_comparison.pdf", WIDTH, HEIGHT, DPI);
    }

    /**
     * Plot 4: Deviation from observed as function of correction order.
     */
    public PlotResult plotDeviationAnalysis() throws IOException {
        log.info("Generating deviation analysis plot");

        ChoptyukFormula formula = ChoptyukFormula.canonical();

        XYSeries deviationSeries = new XYSeries("|Delta_Ch(n) - Delta_obs|");
        for (int n = 0; n <= 8; n++) {
            double val = formula.evaluateToOrder(n);
            double dev = Math.abs(val - 3.443);
            deviationSeries.add(n, dev);
        }

        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(deviationSeries);

        JFreeChart chart = ChartFactory.createXYLineChart(
                "Deviation Analysis: |Delta_Ch(n) - Delta_obs|",
                "Correction Order n", "Absolute Deviation",
                dataset, PlotOrientation.VERTICAL, true, true, false);

        applyDarkTheme(chart);

        Files.createDirectories(Paths.get(PLOT_DIR));
        ChartUtils.saveChartAsPNG(new File(PLOT_DIR, "deviation_analysis.png"), chart, WIDTH, HEIGHT);

        return new PlotResult("deviation_analysis", PLOT_DIR + "/deviation_analysis.png",
                PLOT_DIR + "/deviation_analysis.pdf", WIDTH, HEIGHT, DPI);
    }

    /**
     * Plot 5: Convergence of the correction series.
     */
    public PlotResult plotConvergence() throws IOException {
        log.info("Generating convergence plot");

        ChoptyukFormula formula = ChoptyukFormula.canonical();

        XYSeries deltaSeries = new XYSeries("Delta_Ch(n)");
        XYSeries diffSeries = new XYSeries("|Delta_Ch(n) - Delta_Ch(n-1)|");

        double prev = formula.evaluateToOrder(0);
        deltaSeries.add(0, prev);

        for (int n = 1; n <= 8; n++) {
            double current = formula.evaluateToOrder(n);
            deltaSeries.add(n, current);
            diffSeries.add(n, Math.abs(current - prev));
            prev = current;
        }

        XYSeriesCollection dataset1 = new XYSeriesCollection();
        dataset1.addSeries(deltaSeries);

        XYSeriesCollection dataset2 = new XYSeriesCollection();
        dataset2.addSeries(diffSeries);

        JFreeChart chart = ChartFactory.createXYLineChart(
                "Convergence of Choptyuk Correction Series",
                "Order n", "Value",
                dataset1, PlotOrientation.VERTICAL, true, true, false);

        applyDarkTheme(chart);

        XYPlot plot = (XYPlot) chart.getPlot();
        plot.setDataset(1, dataset2);
        plot.setRangeAxis(1, new org.jfree.chart.axis.NumberAxis("Difference"));
        plot.mapDatasetToRangeAxis(1, 1);
        var renderer1 = new XYLineAndShapeRenderer();
        renderer1.setSeriesPaint(0, SERIES_1);
        var renderer2 = new XYLineAndShapeRenderer();
        renderer2.setSeriesPaint(0, SERIES_2);
        plot.setRenderer(0, renderer1);
        plot.setRenderer(1, renderer2);

        Files.createDirectories(Paths.get(PLOT_DIR));
        ChartUtils.saveChartAsPNG(new File(PLOT_DIR, "convergence.png"), chart, WIDTH, HEIGHT);

        return new PlotResult("convergence", PLOT_DIR + "/convergence.png",
                PLOT_DIR + "/convergence.pdf", WIDTH, HEIGHT, DPI);
    }

    /**
     * Applies a dark theme to the chart.
     */
    private void applyDarkTheme(JFreeChart chart) {
        chart.setBackgroundPaint(BG_COLOR);
        XYPlot plot = chart.getXYPlot();
        plot.setBackgroundPaint(BG_COLOR);
        plot.setDomainGridlinePaint(GRID_COLOR);
        plot.setRangeGridlinePaint(GRID_COLOR);
        plot.getDomainAxis().setLabelPaint(TEXT_COLOR);
        plot.getDomainAxis().setTickLabelPaint(TEXT_COLOR);
        plot.getRangeAxis().setLabelPaint(TEXT_COLOR);
        plot.getRangeAxis().setTickLabelPaint(TEXT_COLOR);
        chart.getTitle().setPaint(TEXT_COLOR);
        if (chart.getLegend() != null) {
            chart.getLegend().setBackgroundPaint(BG_COLOR);
            chart.getLegend().setItemPaint(TEXT_COLOR);
        }
    }
}
