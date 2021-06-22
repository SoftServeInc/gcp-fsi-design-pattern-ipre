import React from "react";
import { Chart, registerables } from "chart.js";

let myChart;

let data = {
  labels: ["Start", "", "", "", "", "", "", "", "", "", "", "", "Year 1"],
  datasets: [
    {
      borderColor: "#FFF",
      data: [10, 12, 14, 15, 18, 20, 22, 24, 27, 30, 34, 38],
      fill: true,
      lineTension: 0.5,
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
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: "#FFF",
        },
      },
      y: {
        display: false,
        grid: {
          display: false,
        },
      },
    },
  },
};

const RoRChart = ({ value, rateOfReturn }) => {
  const chartRef = React.useRef();

  const calculateMonthlyReturn = (value, rateOfReturn) => {
    const PERCENTAGE = 0.01;

    const initialAmount = parseInt(value, 10);
    const amountAfterYear = Math.floor(
      initialAmount + initialAmount * (rateOfReturn * PERCENTAGE)
    );

    const returnByMonth = [initialAmount];
    const averageMonthlyReturn = Math.floor(
      (1 / 12) * (amountAfterYear - initialAmount)
    );

    for (let i = 1; i <= 12; i++) {
      const prevMonthValue = returnByMonth[i - 1];
      const currentMonthValue = prevMonthValue + averageMonthlyReturn;

      returnByMonth.push(currentMonthValue);
    }

    return returnByMonth;
  };

  const values = calculateMonthlyReturn(value, rateOfReturn);

  data.datasets[0].data = values;

  React.useEffect(() => {
    const myChartRef = chartRef.current.getContext("2d");

    if (typeof myChart !== "undefined") {
      myChart.destroy();
    }

    Chart.register(...registerables);

    myChart = new Chart(myChartRef, config);
  });

  return (
    <div>
      <canvas
        id="myChart"
        ref={chartRef}
        height="80"
        style={{
          background:
            "radial-gradient(100% 100% at 100% 0%, #00C078 0%, #2B33A4 100%)",
          borderRadius: "10px",
        }}
      />
    </div>
  );
};

export default RoRChart;
