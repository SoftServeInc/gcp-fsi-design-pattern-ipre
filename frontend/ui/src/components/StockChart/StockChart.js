import React from "react";
import { Chart, registerables } from "chart.js";

let myChart;

let data = {
  labels: [],
  datasets: [
    {
      label: "Price",
      data: [],
      borderColor: "#00C471",
      backgroundColor:
        "linear-gradient(90deg, rgba(0,192,120,1) 0%, rgba(0,0,0,0.20632002801120453) 100%);",
      fill: true,
      pointRadius: 1,
    },
  ],
};

const config = {
  type: "line",
  data: data,
  options: {
    plugins: {
      legend: {
        display: false,
      },
      xAxes: [
        {
          ticks: {
            display: false,
          },
        },
      ],
      filler: {
        propagate: false,
      },
      title: {
        display: false,
      },
    },
    xAxes: [
      {
        ticks: {
          display: false,
        },
      },
    ],
    interaction: {
      intersect: false,
    },
  },
};

const StockChart = ({ history }) => {
  const chartRef = React.useRef();

  React.useEffect(() => {
    const myChartRef = chartRef.current.getContext("2d");
    const gradientFill = myChartRef.createLinearGradient(
      0,
      0,
      0,
      chartRef.current.height
    );

    gradientFill.addColorStop(0, "rgba(0, 192, 120, 1)");
    gradientFill.addColorStop(1, "rgba(0, 192, 120, 0.0001)");

    data.datasets[0].backgroundColor = gradientFill;

    const dataset = Object.values(history);
    const emptyLabels = Array(dataset.length).fill("");

    data.datasets[0].data = dataset;
    data.labels = emptyLabels;

    if (typeof myChart !== "undefined") {
      myChart.destroy();
    }

    Chart.register(...registerables);
    myChart = new Chart(myChartRef, config);
  });

  return (
    <div>
      <canvas id="myChart" ref={chartRef} />
    </div>
  );
};

export default StockChart;
