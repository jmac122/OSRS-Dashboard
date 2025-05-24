import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const GPChart = ({ data, title = "GP/Hour Comparison" }) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y.toLocaleString()} GP/hr`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return value.toLocaleString() + ' GP';
          }
        }
      }
    }
  };

  const chartData = {
    labels: data?.labels || ['No Data'],
    datasets: [
      {
        label: 'GP/Hour',
        data: data?.values || [0],
        backgroundColor: [
          'rgba(255, 215, 0, 0.8)',   // Gold
          'rgba(34, 139, 34, 0.8)',   // Green
          'rgba(220, 20, 60, 0.8)',   // Red
          'rgba(139, 69, 19, 0.8)',   // Brown
        ],
        borderColor: [
          'rgba(255, 215, 0, 1)',
          'rgba(34, 139, 34, 1)',
          'rgba(220, 20, 60, 1)',
          'rgba(139, 69, 19, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  return (
    <div className="w-full h-64">
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default GPChart; 