import React, { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

const Dashboard = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/api/rfm").then((res) => setData(res.data));
  }, []);

  return (
    <div>
      <h2>RFM Customer Clusters</h2>
      <BarChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="CustomerID" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="Recency" fill="#8884d8" />
        <Bar dataKey="Frequency" fill="#82ca9d" />
        <Bar dataKey="Monetary" fill="#ffc658" />
      </BarChart>
    </div>
  );
};

export default Dashboard;
