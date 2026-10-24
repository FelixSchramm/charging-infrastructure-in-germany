import { useEffect, useRef } from "react";
import * as echarts from "echarts";

/**
 * Bar chart wrapper around ECharts that resizes with its container.
 * @param {object} props.option - ECharts option object.
 */
export default function BarChart({ option }) {
  const ref = useRef(null);
  const chart = useRef(null);

  useEffect(() => {
    chart.current = echarts.init(ref.current);
    const observer = new ResizeObserver(() => chart.current.resize());
    observer.observe(ref.current);
    return () => {
      observer.disconnect();
      chart.current.dispose();
    };
  }, []);

  useEffect(() => {
    // notMerge drops series of deselected categories.
    chart.current.setOption(option, { notMerge: true });
  }, [option]);

  return <div ref={ref} className="chart" />;
}
